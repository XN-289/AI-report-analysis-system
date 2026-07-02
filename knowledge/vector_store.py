"""
向量知识库 - 使用sentence-transformers + faiss实现语义搜索
"""
import json
import sqlite3
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, db_path="data/reports.db", model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.db_path = db_path
        self.model_name = model_name
        self.model = None
        self.index = None
        self.id_map = []
        self._init_db()

    def _get_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"加载模型: {self.model_name}")
            except ImportError:
                logger.warning("sentence-transformers未安装，向量搜索不可用")
                return None
        return self.model

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                org_name TEXT,
                publish_date TEXT,
                industry_name TEXT,
                pdf_url TEXT,
                rating TEXT,
                sentiment TEXT,
                confidence INTEGER DEFAULT 0,
                one_liner TEXT,
                key_points TEXT,
                risks TEXT,
                stocks TEXT,
                key_data TEXT,
                trend TEXT,
                summary TEXT,
                html_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS reports_fts
            USING fts5(title, summary, key_points, one_liner, content=reports, content_rowid=id)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                report_id INTEGER PRIMARY KEY,
                embedding BLOB,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            )
        """)
        conn.commit()
        conn.close()

    def add_report(self, report_data):
        """添加研报到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            INSERT INTO reports (title, org_name, publish_date, industry_name, pdf_url,
                rating, sentiment, confidence, one_liner, key_points, risks, stocks,
                key_data, trend, summary, html_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_data.get("title", ""),
            report_data.get("org_name", ""),
            report_data.get("publish_date", ""),
            report_data.get("industry_name", ""),
            report_data.get("pdf_url", ""),
            report_data.get("rating", ""),
            report_data.get("sentiment", "neutral"),
            report_data.get("confidence", 0),
            report_data.get("one_liner", ""),
            json.dumps(report_data.get("key_points", []), ensure_ascii=False),
            json.dumps(report_data.get("risks", []), ensure_ascii=False),
            json.dumps(report_data.get("stocks", []), ensure_ascii=False),
            json.dumps(report_data.get("key_data", {}), ensure_ascii=False),
            report_data.get("trend", ""),
            report_data.get("summary", ""),
            report_data.get("html_path", "")
        ))
        report_id = cursor.lastrowid

        # Update FTS index
        conn.execute("""
            INSERT INTO reports_fts(rowid, title, summary, key_points, one_liner)
            VALUES (?, ?, ?, ?, ?)
        """, (
            report_id,
            report_data.get("title", ""),
            report_data.get("summary", ""),
            json.dumps(report_data.get("key_points", []), ensure_ascii=False),
            report_data.get("one_liner", "")
        ))
        conn.commit()
        conn.close()

        # Generate and store embedding
        self._generate_embedding(report_id, report_data)
        return report_id

    def _generate_embedding(self, report_id, report_data):
        """生成并存储embedding"""
        model = self._get_model()
        if not model:
            return

        text = " ".join([
            report_data.get("title", ""),
            report_data.get("one_liner", ""),
            " ".join(report_data.get("key_points", []))
        ])

        try:
            import numpy as np
            embedding = model.encode(text)
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT OR REPLACE INTO embeddings (report_id, embedding) VALUES (?, ?)",
                (report_id, embedding.tobytes())
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"生成embedding失败: {e}")

    def search(self, query, top_k=10):
        """语义搜索"""
        model = self._get_model()
        if not model:
            return self.fts_search(query, top_k)

        try:
            import numpy as np
            import faiss

            query_vec = model.encode(query).reshape(1, -1)

            # Load all embeddings
            conn = sqlite3.connect(self.db_path)
            rows = conn.execute("SELECT report_id, embedding FROM embeddings").fetchall()
            conn.close()

            if not rows:
                return self.fts_search(query, top_k)

            ids = [r[0] for r in rows]
            vectors = np.vstack([np.frombuffer(r[1], dtype=np.float32) for r in rows])

            # Build FAISS index
            dim = vectors.shape[1]
            index = faiss.IndexFlatIP(dim)
            faiss.normalize_L2(vectors)
            index.add(vectors)

            # Search
            faiss.normalize_L2(query_vec)
            scores, indices = index.search(query_vec, min(top_k, len(ids)))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0:
                    continue
                report_id = ids[idx]
                report = self.get_report(report_id)
                if report:
                    report["similarity"] = float(score)
                    results.append(report)

            return results
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return self.fts_search(query, top_k)

    def fts_search(self, query, top_k=10):
        """全文搜索 - 使用LIKE查询（中文友好）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            like_pattern = f"%{query}%"
            rows = conn.execute("""
                SELECT * FROM reports
                WHERE title LIKE ? OR org_name LIKE ? OR industry_name LIKE ?
                    OR summary LIKE ? OR one_liner LIKE ? OR key_points LIKE ?
                ORDER BY publish_date DESC LIMIT ?
            """, (like_pattern, like_pattern, like_pattern,
                  like_pattern, like_pattern, like_pattern, top_k)).fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
        finally:
            conn.close()

    def get_report(self, report_id):
        """获取单篇研报"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        conn.close()
        if row:
            result = dict(row)
            for field in ["key_points", "risks", "stocks", "key_data"]:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except:
                        pass
            return result
        return None

    def get_reports(self, page=1, per_page=20, industry=None, rating=None, time_filter=None, query=None):
        """获取研报列表（带筛选）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        conditions = ["1=1"]
        params = []

        if industry:
            conditions.append("industry_name = ?")
            params.append(industry)
        if rating:
            conditions.append("rating = ?")
            params.append(rating)
        if time_filter == "today":
            conditions.append("publish_date = date('now')")
        elif time_filter == "week":
            conditions.append("publish_date >= date('now', '-7 days')")
        elif time_filter == "month":
            conditions.append("publish_date >= date('now', '-30 days')")
        if query:
            conditions.append("(title LIKE ? OR summary LIKE ? OR one_liner LIKE ?)")
            params.extend([f"%{query}%"] * 3)

        where = " AND ".join(conditions)
        offset = (page - 1) * per_page

        total = conn.execute(f"SELECT COUNT(*) FROM reports WHERE {where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM reports WHERE {where} ORDER BY publish_date DESC LIMIT ? OFFSET ?",
            params + [per_page, offset]
        ).fetchall()
        conn.close()

        results = []
        for row in rows:
            result = dict(row)
            for field in ["key_points", "risks", "stocks", "key_data"]:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except:
                        pass
            results.append(result)

        return {"total": total, "page": page, "per_page": per_page, "reports": results}

    def get_stats(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        today = conn.execute("SELECT COUNT(*) FROM reports WHERE publish_date = date('now')").fetchone()[0]
        industries = conn.execute(
            "SELECT industry_name, COUNT(*) as cnt FROM reports WHERE industry_name != '' GROUP BY industry_name ORDER BY cnt DESC LIMIT 10"
        ).fetchall()
        ratings = conn.execute(
            "SELECT rating, COUNT(*) as cnt FROM reports WHERE rating != '' GROUP BY rating ORDER BY cnt DESC"
        ).fetchall()
        conn.close()

        return {
            "total_reports": total,
            "today_reports": today,
            "top_industries": [{"name": r[0], "count": r[1]} for r in industries],
            "rating_distribution": [{"rating": r[0], "count": r[1]} for r in ratings]
        }

    def get_industries(self):
        """获取所有行业列表"""
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT DISTINCT industry_name FROM reports WHERE industry_name != '' ORDER BY industry_name"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]

    def report_exists(self, title, publish_date):
        """检查研报是否已存在"""
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT id FROM reports WHERE title = ? AND publish_date = ?",
            (title, publish_date)
        ).fetchone()
        conn.close()
        return row is not None

    def rebuild_embeddings(self):
        """重建所有embedding"""
        model = self._get_model()
        if not model:
            return

        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT id, title, one_liner, key_points FROM reports").fetchall()

        # Clear existing embeddings
        conn.execute("DELETE FROM embeddings")
        conn.commit()

        import numpy as np
        for row in rows:
            text = " ".join([row[1] or "", row[2] or "", row[3] or ""])
            embedding = model.encode(text)
            conn.execute(
                "INSERT INTO embeddings (report_id, embedding) VALUES (?, ?)",
                (row[0], embedding.tobytes())
            )

        conn.commit()
        conn.close()
        logger.info(f"重建了 {len(rows)} 条embedding")
