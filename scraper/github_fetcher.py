"""
GitHub数据爬取器 - 从manymore13/report仓库获取研报数据
"""
import requests
import json
import csv
import io
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/manymore13/report/main"

class GitHubFetcher:
    def __init__(self, base_url=GITHUB_RAW_BASE):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def _get(self, url, timeout=15):
        try:
            resp = self.session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp
        except Exception as e:
            logger.error(f"请求失败: {url} - {e}")
            return None

    def fetch_month_reports(self):
        """获取本月研报列表"""
        url = f"{self.base_url}/eastmoney/month.json"
        resp = self._get(url)
        if not resp:
            return []
        try:
            data = resp.json()
            reports = []
            for item in data:
                reports.append({
                    "title": item.get("title", ""),
                    "org_name": item.get("org_name", ""),
                    "publish_date": item.get("publish_date", ""),
                    "industry_name": item.get("industry_name", ""),
                    "pdf_url": item.get("pdf_url", ""),
                    "source": "github_month"
                })
            return reports
        except Exception as e:
            logger.error(f"解析month.json失败: {e}")
            return []

    def fetch_today_reports(self):
        """获取今日研报（从today.md解析）"""
        url = f"{self.base_url}/eastmoney/today.md"
        resp = self._get(url)
        if not resp:
            return []
        try:
            text = resp.text
            reports = []
            # Parse markdown table format
            lines = text.split("\n")
            for line in lines:
                if "|" in line and ("研报" in line or "报告" in line or "分析" in line or "策略" in line):
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 3:
                        reports.append({
                            "title": parts[0],
                            "org_name": parts[1] if len(parts) > 1 else "",
                            "publish_date": datetime.now().strftime("%Y-%m-%d"),
                            "industry_name": parts[2] if len(parts) > 2 else "",
                            "pdf_url": "",
                            "source": "github_today"
                        })
            return reports
        except Exception as e:
            logger.error(f"解析today.md失败: {e}")
            return []

    def fetch_industry_reports(self, industry_name):
        """获取特定行业研报"""
        url = f"{self.base_url}/eastmoney/{industry_name}.csv"
        resp = self._get(url)
        if not resp:
            return []
        try:
            content = resp.content.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            reports = []
            for row in reader:
                reports.append({
                    "title": row.get("title", ""),
                    "org_name": row.get("org_name", ""),
                    "publish_date": row.get("publish_date", ""),
                    "industry_name": industry_name,
                    "pdf_url": row.get("pdf_url", ""),
                    "source": "github_industry"
                })
            return reports
        except Exception as e:
            logger.error(f"解析{industry_name}.csv失败: {e}")
            return []

    def fetch_index_data(self):
        """获取指数估值数据"""
        url = f"{self.base_url}/index_data.json"
        resp = self._get(url)
        if not resp:
            return []
        try:
            return resp.json()
        except Exception as e:
            logger.error(f"解析index_data.json失败: {e}")
            return []

    def get_available_industries(self):
        """获取可用行业列表"""
        industries = [
            "半导体", "游戏", "银行", "证券", "保险", "房地产开发", "光伏设备",
            "风电设备", "电池", "消费电子", "汽车零部件", "白酒", "中药",
            "生物制品", "医药商业", "医疗服务", "医疗器械", "化学制药",
            "软件开发", "IT服务", "通信设备", "通信服务", "计算机设备",
            "电力", "煤炭开采", "石油石化", "化学制品", "钢铁",
            "有色金属", "建筑材料", "建筑装饰", "交通运输", "物流",
            "食品加工", "休闲食品", "饮料乳品", "服装家纺", "家用电器",
            "轻工制造", "纺织服饰", "美容护理", "商贸零售", "社会服务",
            "农林牧渔", "国防军工", "机械设备", "环保", "公用事业",
            "综合", "传媒", "电子", "非银金融", "房地产服务"
        ]
        return industries
