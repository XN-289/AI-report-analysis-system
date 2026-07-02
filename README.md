# 🏛️ 研报智库 — AI 智能券商研报分析平台

> **每日精选券商研报，AI 智能解析，一目了然**

在线访问：**https://xn-289.github.io/AI-report-analysis-system/**

---

## ✨ 项目特色

- 📊 **1300+ 篇研报** — 覆盖 50+ 行业，每日自动更新
- 🤖 **AI 智能解析** — DeepSeek 提取核心观点、评级、风险提示
- 🎨 **精美卡片** — 清晰的信息层次，一键查看原文 PDF
- 🔍 **智能搜索** — 支持关键词、行业、评级多维筛选
- 🌙 **暗色模式** — 护眼阅读体验
- 📱 **响应式设计** — 桌面、平板、手机完美适配

---

## 🆓 关于 GitHub Pages — 完全免费

| 项目 | 说明 |
|------|------|
| **费用** | ✅ **完全免费**，无需任何付费 |
| **流量限制** | 每月 100GB 带宽（个人项目完全够用） |
| **存储限制** | 仓库最大 1GB |
| **域名** | 免费提供 `username.github.io` 子域名 |
| **自定义域名** | 支持绑定自己的域名（可选） |
| **HTTPS** | ✅ 自动启用，安全加密 |
| **构建** | 自动部署，推送代码即上线 |

**简单来说**：GitHub Pages 是 GitHub 提供的免费静态网站托管服务。你只需要一个 GitHub 账号，把代码推上去，就能获得一个永久可访问的网站。没有服务器费用，没有运维成本。

**代价**：
- 仅支持静态网站（HTML/CSS/JS），不能运行后端代码
- 每月 100GB 流量限制（对于研报浏览完全足够）
- 仓库大小建议不超过 1GB

---

## 🚀 快速开始

### 方式一：直接访问（推荐）

打开浏览器访问：
**https://xn-289.github.io/AI-report-analysis-system/**

无需安装任何东西，即可浏览最新研报。

### 方式二：本地运行（完整功能）

```bash
# 克隆仓库
git clone git@github.com:XN-289/AI-report-analysis-system.git
cd AI-report-analysis-system

# 安装依赖
pip install -r requirements.txt

# 配置 API Key（可选，启用 AI 解析）
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 运行构建脚本
python build.py --today

# 启动本地服务器
python app.py
# 访问 http://localhost:5000
```

---

## 📁 项目结构

```
├── docs/                    # GitHub Pages 静态站点
│   ├── index.html          # 首页（研报卡片浏览）
│   └── report.html         # 研报详情页（AI 解析结果）
├── scraper/                # 数据爬取
│   ├── github_fetcher.py   # GitHub 仓库数据
│   └── eastmoney_api.py    # 东方财富 API
├── parser/
│   └── report_parser.py    # AI 结构化解析
├── knowledge/
│   └── vector_store.py     # 向量知识库
├── templates/              # Jinja2 模板（本地 Flask 使用）
├── app.py                  # Flask 本地服务器
├── build.py                # 自动化构建脚本
└── requirements.txt        # Python 依赖
```

---

## 🔧 技术栈

| 层 | 技术 |
|----|------|
| 前端 | 原生 HTML/CSS/JS，响应式设计 |
| 后端 | Flask（本地运行时） |
| AI 解析 | DeepSeek API |
| 数据源 | manymore13/report + 东方财富 |
| 向量搜索 | sentence-transformers + FAISS |
| 部署 | GitHub Pages（免费） |

---

## 📊 数据来源

- [manymore13/report](https://github.com/manymore13/report) — 每日更新的券商研报数据库
- [东方财富](https://www.eastmoney.com/) — 中国最大的财经数据平台

---

## 📝 License

MIT License

---

## 🙏 致谢

- [manymore13](https://github.com/manymore13) — 研报数据源
- [东方财富](https://www.eastmoney.com/) — 数据平台
- [DeepSeek](https://deepseek.com/) — AI 模型
