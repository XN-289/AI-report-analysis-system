"""
AI结构化解析器 - 使用LLM解析研报内容
"""
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

PARSE_PROMPT = """你是一个专业的金融研报分析师。请对以下研报进行结构化分析。

研报信息：
- 标题：{title}
- 券商：{org_name}
- 行业：{industry}
- 摘要：{summary}

请严格按以下JSON格式输出分析结果（不要输出其他内容）：
{{
    "key_points": ["观点1", "观点2", "观点3"],
    "rating": "买入/增持/中性/减持/卖出/无评级",
    "target_price": "目标价（如有）",
    "risks": ["风险1", "风险2"],
    "trend": "行业趋势判断",
    "stocks": ["提及的股票1", "提及的股票2"],
    "key_data": {{"指标名": "数值"}},
    "one_liner": "一句话摘要（30字以内）",
    "sentiment": "bullish/bearish/neutral",
    "confidence": 75
}}

要求：
1. key_points 提取3-5个核心观点，每个不超过50字
2. rating 根据内容判断，如无明确评级则填"无评级"
3. risks 提取2-3个风险点
4. one_liner 必须30字以内，精炼概括核心结论
5. confidence 0-100，表示分析置信度
6. 如果信息不足，合理推断但保持保守"""

DIGEST_PROMPT = """你是专业的金融分析师。请根据今日研报数据，生成一份简洁的每日市场研报摘要。

今日研报数据：
{reports_summary}

请输出：
1. 市场整体观点（2-3句话）
2. 热门行业（列出被研报覆盖最多的3个行业及核心观点）
3. 值得关注的个股（2-3只，含券商评级）
4. 风险提示（1-2个主要风险）

格式要求：简洁有力，适合快速阅读，总字数控制在300字以内。"""

class ReportParser:
    def __init__(self, api_key, base_url="https://api.deepseek.com"):
        if not api_key:
            logger.warning("未配置API Key，AI解析功能不可用")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def parse_report(self, title, summary="", org_name="", industry=""):
        """解析单篇研报"""
        if not self.client:
            return self._default_result()

        prompt = PARSE_PROMPT.format(
            title=title,
            org_name=org_name,
            industry=industry,
            summary=summary[:600] if summary else "无摘要"
        )

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            content = response.choices[0].message.content
            # Extract JSON from response
            if "{" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                result = json.loads(content[start:end])
                return self._validate_result(result)
            return self._default_result()
        except Exception as e:
            logger.error(f"AI解析失败: {title} - {e}")
            return self._default_result()

    def batch_parse(self, reports, max_concurrent=3):
        """批量解析研报"""
        results = []
        for i, report in enumerate(reports):
            logger.info(f"解析 [{i+1}/{len(reports)}] {report.get('title', '')[:30]}...")
            result = self.parse_report(
                title=report.get("title", ""),
                summary=report.get("summary", ""),
                org_name=report.get("org_name", ""),
                industry=report.get("industry_name", "")
            )
            result.update({
                "original_title": report.get("title", ""),
                "org_name": report.get("org_name", ""),
                "publish_date": report.get("publish_date", ""),
                "industry_name": report.get("industry_name", ""),
                "pdf_url": report.get("pdf_url", ""),
                "rating": report.get("rating") or result.get("rating", "无评级")
            })
            results.append(result)
        return results

    def generate_daily_digest(self, parsed_reports):
        """生成每日研报摘要"""
        if not self.client or not parsed_reports:
            return "今日暂无研报数据"

        summary_parts = []
        for r in parsed_reports[:20]:
            summary_parts.append(
                f"- {r.get('original_title', '')} | {r.get('org_name', '')} | "
                f"评级:{r.get('rating', '无')} | {r.get('one_liner', '')}"
            )

        prompt = DIGEST_PROMPT.format(reports_summary="\n".join(summary_parts))

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return "摘要生成失败"

    def _validate_result(self, result):
        defaults = self._default_result()
        for key, default_val in defaults.items():
            if key not in result:
                result[key] = default_val
        if not isinstance(result["key_points"], list):
            result["key_points"] = [str(result["key_points"])]
        if not isinstance(result["risks"], list):
            result["risks"] = [str(result["risks"])]
        if not isinstance(result["stocks"], list):
            result["stocks"] = []
        result["confidence"] = min(100, max(0, int(result.get("confidence", 50))))
        return result

    def _default_result(self):
        return {
            "key_points": ["暂无分析"],
            "rating": "无评级",
            "target_price": "",
            "risks": ["暂无风险提示"],
            "trend": "暂无趋势判断",
            "stocks": [],
            "key_data": {},
            "one_liner": "暂无摘要",
            "sentiment": "neutral",
            "confidence": 0
        }
