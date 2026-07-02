"""
研报分析系统 - 自动化构建脚本
流程：爬取数据 → AI解析 → 生成HTML → 更新知识库
"""
import argparse
import logging
from datetime import datetime
from scraper.github_fetcher import GitHubFetcher
from scraper.eastmoney_api import EastMoneyAPI
from parser.report_parser import ReportParser
from knowledge.vector_store import VectorStore
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, OUTPUT_DIR, TEMPLATES_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="研报分析系统构建脚本")
    parser.add_argument("--today", action="store_true", help="只处理今日研报")
    parser.add_argument("--month", action="store_true", help="处理本月研报")
    parser.add_argument("--industry", type=str, help="处理特定行业")
    parser.add_argument("--rebuild-vectors", action="store_true", help="重建向量索引")
    parser.add_argument("--no-ai", action="store_true", help="跳过AI解析")
    args = parser.parse_args()

    github = GitHubFetcher()
    eastmoney = EastMoneyAPI()
    ai_parser = ReportParser(DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL)
    store = VectorStore()

    # Step 1: Fetch reports
    logger.info("=" * 50)
    logger.info("步骤 1/4: 爬取研报数据")
    reports = []

    if args.today:
        reports = github.fetch_today_reports()
    elif args.month:
        reports = github.fetch_month_reports()
    elif args.industry:
        reports = github.fetch_industry_reports(args.industry)
    else:
        # Default: fetch today's reports
        reports = github.fetch_today_reports()
        if not reports:
            reports = github.fetch_month_reports()

    logger.info(f"获取到 {len(reports)} 篇研报")

    # Deduplicate
    new_reports = []
    for r in reports:
        if not store.report_exists(r["title"], r["publish_date"]):
            new_reports.append(r)
    logger.info(f"去重后新增 {len(new_reports)} 篇")

    # Step 2: AI parsing
    logger.info("=" * 50)
    logger.info("步骤 2/4: AI结构化解析")
    if args.no_ai or not DEEPSEEK_API_KEY:
        logger.info("跳过AI解析（未配置API Key或使用--no-ai）")
        parsed = []
        for r in new_reports:
            parsed.append({
                **r,
                "key_points": [],
                "risks": [],
                "stocks": [],
                "one_liner": "",
                "sentiment": "neutral",
                "confidence": 0,
                "rating": r.get("rating", "无评级"),
                "trend": "",
                "key_data": {},
            })
    else:
        parsed = ai_parser.batch_parse(new_reports)

    # Step 3: Generate HTML and save to DB
    logger.info("=" * 50)
    logger.info("步骤 3/4: 生成HTML并存入数据库")
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")

    for report_data in parsed:
        html_content = template.render(report=report_data)
        filename = (
            f"{report_data.get('publish_date', 'unknown')}_"
            f"{report_data.get('title', '')[:30].replace('/', '_')}.html"
        )
        html_path = OUTPUT_DIR / filename
        html_path.write_text(html_content, encoding="utf-8")
        report_data["html_path"] = str(html_path)
        store.add_report(report_data)

    logger.info(f"已生成 {len(parsed)} 份HTML报告")

    # Step 4: Generate index page
    logger.info("=" * 50)
    logger.info("步骤 4/4: 生成首页")
    index_template = env.get_template("index.html")
    stats = store.get_stats()
    all_reports = store.get_reports(per_page=50)["reports"]
    industries = store.get_industries()
    pagination = {
        "page": 1,
        "per_page": 50,
        "total": stats["total_reports"],
        "has_prev": False,
        "has_next": False,
        "pages": 1,
    }
    filters = {"query": "", "industry": "", "time": "", "rating": ""}
    index_html = index_template.render(
        reports=all_reports,
        stats=stats,
        industries=industries,
        pagination=pagination,
        filters=filters,
    )
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    logger.info(f"首页已生成: {index_path}")

    # Generate digest
    if parsed and DEEPSEEK_API_KEY:
        logger.info("生成每日摘要...")
        digest = ai_parser.generate_daily_digest(parsed)
        digest_path = OUTPUT_DIR / f"digest_{datetime.now().strftime('%Y%m%d')}.md"
        digest_path.write_text(digest, encoding="utf-8")

    logger.info("=" * 50)
    logger.info("构建完成！")
    logger.info(f"报告目录: {OUTPUT_DIR}")
    logger.info(f"启动服务: python app.py")


if __name__ == "__main__":
    main()
