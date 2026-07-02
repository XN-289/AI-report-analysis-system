"""
东方财富API爬取器 - 获取研报详情和更多数据
"""
import requests
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

EASTMONEY_API = "https://reportapi.eastmoney.com"

class EastMoneyAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def _get(self, url, params=None, timeout=12):
        try:
            resp = self.session.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"API请求失败: {url} - {e}")
            return None

    def _post(self, url, data=None, timeout=12):
        try:
            resp = self.session.post(url, json=data, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"API POST请求失败: {url} - {e}")
            return None

    def fetch_industry_reports(self, industry_code, page=1, page_size=20):
        """获取行业研报"""
        today = datetime.now().strftime("%Y-%m-%d")
        params = {
            "pageSize": page_size,
            "pageNo": page,
            "beginTime": "2025-01-01",
            "endTime": today,
            "qType": 1,
            "industryCode": industry_code,
            "industry": "*",
            "rating": "*"
        }
        data = self._get(f"{EASTMONEY_API}/report/list", params=params)
        return self._parse_reports(data)

    def fetch_stock_reports(self, stock_code, page=1, page_size=20):
        """获取个股研报"""
        today = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "pageSize": page_size,
            "pageNo": page,
            "beginTime": "2025-01-01",
            "endTime": today,
            "code": stock_code
        }
        data = self._post(f"{EASTMONEY_API}/report/list2", data=payload)
        return self._parse_reports(data)

    def fetch_strategy_reports(self, page=1, page_size=20):
        """获取策略报告"""
        return self._fetch_type_reports(2, page, page_size)

    def fetch_macro_reports(self, page=1, page_size=20):
        """获取宏观研究"""
        return self._fetch_type_reports(3, page, page_size)

    def fetch_morning_reports(self, page=1, page_size=20):
        """获取券商晨报"""
        return self._fetch_type_reports(4, page, page_size)

    def _fetch_type_reports(self, q_type, page, page_size):
        today = datetime.now().strftime("%Y-%m-%d")
        params = {
            "pageSize": page_size,
            "pageNo": page,
            "beginTime": "2025-01-01",
            "endTime": today,
            "qType": q_type
        }
        data = self._get(f"{EASTMONEY_API}/report/jg", params=params)
        return self._parse_reports(data)

    def _parse_reports(self, data):
        if not data or "data" not in data:
            return []
        reports = []
        for item in (data.get("data") or []):
            reports.append({
                "title": item.get("title", ""),
                "org_name": item.get("orgSName", ""),
                "publish_date": item.get("publishDate", ""),
                "industry_name": item.get("industryName", ""),
                "stock_name": item.get("stockName", ""),
                "rating": item.get("emRatingName", ""),
                "pages": item.get("attachPages"),
                "encode_url": item.get("encodeUrl", ""),
                "info_code": item.get("infoCode", ""),
                "pdf_url": "",
                "source": "eastmoney_api"
            })
        return reports

    def fetch_report_detail(self, encode_url, report_type="industry"):
        """获取研报详情页内容"""
        type_map = {
            "industry": "zw_industry",
            "stock": "zw_stock",
            "strategy": "zw_macresearch",
            "macro": "zw_macresearch",
            "morning": "zw_macresearch"
        }
        page_type = type_map.get(report_type, "zw_industry")
        url = f"https://data.eastmoney.com/report/{page_type}.jshtml?encodeUrl={encode_url}"

        try:
            resp = self.session.get(url, timeout=12)
            resp.raise_for_status()
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")

            # Extract summary text
            paragraphs = soup.find_all("p")
            summary = ""
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 20:
                    summary += text + "\n"
                    if len(summary) > 800:
                        break

            # Extract PDF link
            pdf_link = ""
            pdf_a = soup.select_one("a.pdf-link")
            if pdf_a:
                pdf_link = pdf_a.get("href", "")
            else:
                import re
                match = re.search(r'https://pdf\.dfcfw\.com/pdf/[^\s"\'<>]+\.pdf', resp.text)
                if match:
                    pdf_link = match.group(0)

            return {
                "summary": summary[:800],
                "pdf_url": pdf_link,
                "page_url": url
            }
        except Exception as e:
            logger.error(f"获取详情失败: {url} - {e}")
            return {"summary": "", "pdf_url": "", "page_url": url}

    INDUSTRY_CODES = {
        "半导体": "1036", "游戏": "1046", "银行": "475", "证券": "473",
        "保险": "474", "房地产开发": "451", "光伏设备": "1031",
        "风电设备": "1032", "电池": "1033", "消费电子": "1037",
        "汽车零部件": "481", "白酒": "1277", "中药": "1040",
        "生物制品": "1044", "医药商业": "1042", "医疗服务": "727",
        "化学制药": "465", "软件开发": "737", "IT服务": "1238",
        "通信设备": "448", "通信服务": "736", "电力": "428",
        "煤炭开采": "1250", "化学制品": "538", "通用设备": "545",
        "物流": "422", "电网设备": "457", "元件": "459"
    }
