# 研报智库 - AI驱动的券商研报分析平台

## 项目介绍

研报智库是一个基于 AI 的券商研报智能分析系统，能够自动爬取、解析、存储和检索券商研究报告。系统利用 DeepSeek 大模型对研报内容进行结构化分析，生成可视化 HTML 报告，并通过向量知识库实现语义搜索，帮助用户快速获取研报中的关键信息。

### 核心价值

- **自动化采集**：自动爬取主流券商研报，减少人工收集成本
- **AI 深度解析**：利用大模型提取研报核心观点、财务数据和投资建议
- **可视化呈现**：将结构化数据转换为美观的 HTML 报告
- **智能检索**：基于语义的向量搜索，精准定位相关研报内容
- **知识积累**：构建企业级研报知识库，支持持续学习和分析

## 功能特性

### 1. 数据爬取
- 支持多家主流券商研报平台
- 定时自动爬取，保持数据更新
- 反爬策略处理，确保稳定采集
- 支持手动触发爬取任务

### 2. AI 解析
- DeepSeek 大模型驱动的内容分析
- 自动提取研报关键信息：
  - 公司基本信息
  - 财务数据摘要
  - 核心投资观点
  - 风险提示
  - 评级和目标价
- 支持多种研报格式（PDF、HTML）

### 3. 可视化 HTML 报告
- 自动生成美观的响应式 HTML 页面
- 数据图表可视化展示
- 支持自定义报告模板
- 一键导出和分享

### 4. 语义搜索
- 基于 sentence-transformers 的向量化
- FAISS 高效向量索引
- 支持自然语言查询
- 相关性排序和过滤

### 5. 向量知识库
- 自动构建和更新知识库
- 支持增量更新
- 多维度索引（公司、行业、日期）
- 持久化存储

## 快速开始

### 系统要求

- Python 3.9+
- 内存 4GB+（推荐 8GB）
- 磁盘空间 2GB+（用于向量索引）

### 安装步骤

#### 方式一：Windows 快速启动

```bash
# 克隆项目
git clone <repository-url>
cd 研报智库

# 运行启动脚本
start.bat
```

启动脚本会自动完成：
1. 创建 Python 虚拟环境
2. 安装依赖包
3. 配置环境变量
4. 启动服务

#### 方式二：手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 DEEPSEEK_API_KEY

# 5. 启动服务
python app.py
```

#### 方式三：Docker 部署

```bash
# 构建镜像
docker build -t research-ai .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  --name research-ai \
  research-ai
```

### 配置说明

在 `.env` 文件中配置以下参数：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# 应用配置
APP_PORT=5000
APP_DEBUG=false

# 爬虫配置
CRAWL_INTERVAL=3600  # 爬取间隔（秒）
MAX_CONCURRENT=5     # 最大并发数

# 向量库配置
VECTOR_MODEL=shibing624/text2vec-base-chinese
VECTOR_DIM=768
```

## 架构说明

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    研报智库系统架构                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│   │  爬虫模块 │───▶│  解析模块 │───▶│  存储模块 │         │
│   └──────────┘    └──────────┘    └──────────┘         │
│        │               │               │               │
│        ▼               ▼               ▼               │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│   │ 定时任务  │    │ AI 分析  │    │ 向量索引  │         │
│   └──────────┘    └──────────┘    └──────────┘         │
│                                       │               │
│                                       ▼               │
│                               ┌──────────────┐         │
│                               │   Web 服务    │         │
│                               │  Flask API   │         │
│                               └──────────────┘         │
│                                       │               │
│                                       ▼               │
│                               ┌──────────────┐         │
│                               │   前端界面    │         │
│                               │   HTML/JS    │         │
│                               └──────────────┘         │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```
1. 爬取阶段
   券商网站 ──▶ 爬虫程序 ──▶ 原始数据（PDF/HTML）

2. 解析阶段
   原始数据 ──▶ 内容提取 ──▶ DeepSeek AI ──▶ 结构化数据（JSON）

3. 生成阶段
   结构化数据 ──▶ 模板渲染 ──▶ HTML 可视化报告

4. 知识库构建
   结构化数据 ──▶ 向量化 ──▶ FAISS 索引 ──▶ 语义搜索
```

### 核心模块

| 模块 | 功能 | 技术实现 |
|------|------|----------|
| crawler/ | 研报爬取 | requests, BeautifulSoup |
| parser/ | 内容解析 | PyPDF2, DeepSeek API |
| generator/ | HTML 生成 | Jinja2 模板 |
| vector/ | 向量化与索引 | sentence-transformers, FAISS |
| api/ | Web 服务 | Flask, RESTful API |
| scheduler/ | 定时任务 | APScheduler |

## 目录结构

```
研报智库/
├── app.py                 # Flask 应用入口
├── start.bat             # Windows 启动脚本
├── Dockerfile            # Docker 构建文件
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量示例
├── README.md             # 项目说明文档
│
├── crawler/              # 爬虫模块
│   ├── __init__.py
│   ├── base.py          # 爬虫基类
│   ├── eastmoney.py     # 东方财富爬虫
│   ├── wind.py          # 万得爬虫
│   └── scheduler.py     # 爬取调度器
│
├── parser/               # 解析模块
│   ├── __init__.py
│   ├── pdf_parser.py    # PDF 解析器
│   ├── html_parser.py   # HTML 解析器
│   └── ai_analyzer.py   # AI 分析器
│
├── generator/            # 生成模块
│   ├── __init__.py
│   ├── html_generator.py # HTML 生成器
│   └── templates/        # HTML 模板
│       ├── report.html
│       └── dashboard.html
│
├── vector/               # 向量模块
│   ├── __init__.py
│   ├── embedder.py      # 文本向量化
│   ├── indexer.py        # 索引管理
│   └── searcher.py       # 语义搜索
│
├── api/                  # API 模块
│   ├── __init__.py
│   ├── routes.py         # 路由定义
│   └── services.py       # 业务逻辑
│
├── models/               # 数据模型
│   ├── __init__.py
│   ├── report.py         # 研报模型
│   └── database.py       # 数据库配置
│
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── logger.py         # 日志工具
│   └── helpers.py        # 辅助函数
│
├── data/                 # 数据目录
│   ├── raw/             # 原始数据
│   ├── parsed/          # 解析后数据
│   └── vectors/         # 向量索引
│
├── output/               # 输出目录
│   └── reports/         # HTML 报告
│
└── tests/                # 测试目录
    ├── test_crawler.py
    ├── test_parser.py
    └── test_vector.py
```

## API 接口说明

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **认证方式**: API Key（Header: `X-API-Key`）

### 接口列表

#### 1. 研报管理

##### GET /api/reports
获取研报列表

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| limit | int | 否 | 每页数量，默认 20 |
| company | string | 否 | 公司名称过滤 |
| industry | string | 否 | 行业过滤 |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "id": "report_001",
        "title": "贵州茅台深度报告",
        "company": "贵州茅台",
        "industry": "白酒",
        "analyst": "张三",
        "date": "2024-01-15",
        "rating": "买入",
        "target_price": 2000,
        "summary": "...",
        "html_url": "/reports/report_001.html"
      }
    ]
  }
}
```

##### GET /api/reports/{id}
获取单个研报详情

##### POST /api/reports/crawl
手动触发爬取任务

**请求体**:
```json
{
  "source": "eastmoney",
  "count": 50,
  "industry": "科技"
}
```

#### 2. AI 分析

##### POST /api/analyze
对研报进行 AI 分析

**请求体**:
```json
{
  "report_id": "report_001",
  "analysis_type": "full"  // full, summary, financial
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "company_info": {
      "name": "贵州茅台",
      "code": "600519",
      "industry": "白酒"
    },
    "financial_summary": {
      "revenue": "1000亿",
      "profit": "500亿",
      "growth": "15%"
    },
    "investment_view": {
      "rating": "买入",
      "target_price": 2000,
      "key_points": ["...", "..."]
    },
    "risks": ["...", "..."]
  }
}
```

#### 3. 语义搜索

##### POST /api/search
语义搜索研报内容

**请求体**:
```json
{
  "query": "新能源汽车电池技术发展趋势",
  "limit": 10,
  "filters": {
    "industry": "新能源",
    "date_range": ["2024-01-01", "2024-12-31"]
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "results": [
      {
        "report_id": "report_002",
        "title": "宁德时代深度报告",
        "relevance_score": 0.95,
        "matched_content": "...",
        "highlight": "..."
      }
    ],
    "total": 15
  }
}
```

#### 4. 知识库管理

##### POST /api/knowledge/build
构建/更新向量知识库

##### GET /api/knowledge/stats
获取知识库统计信息

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total_documents": 1000,
    "total_vectors": 50000,
    "index_size": "2.5GB",
    "last_updated": "2024-01-15 10:30:00"
  }
}
```

#### 5. 系统管理

##### GET /api/system/status
系统状态检查

##### GET /api/system/tasks
获取任务队列状态

### 错误响应

```json
{
  "code": 400,
  "error": "Invalid parameter",
  "message": "参数 'page' 必须为正整数"
}
```

**错误码说明**:
| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 部署指南

### 本地开发部署

```bash
# 1. 克隆代码
git clone <repository-url>
cd 研报智库

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 初始化数据库
python init_db.py

# 5. 启动开发服务器
python app.py
```

### 生产环境部署

#### 方式一：Gunicorn + Nginx

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/static;
        expires 30d;
    }
}
```

#### 方式二：Docker Compose

创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

启动服务：
```bash
docker-compose up -d
```

#### 方式三：云服务器部署

**阿里云 ECS 部署示例**：

```bash
# 1. 登录服务器
ssh root@your-server-ip

# 2. 安装 Docker
curl -fsSL https://get.docker.com | sh

# 3. 克隆代码
git clone <repository-url>
cd 研报智库

# 4. 配置环境变量
cp .env.example .env
vi .env

# 5. 启动服务
docker-compose up -d

# 6. 配置防火墙
ufw allow 5000
```

### 环境变量配置

生产环境建议使用以下配置：

```env
# 应用配置
APP_PORT=5000
APP_DEBUG=false
APP_SECRET_KEY=your-secret-key-here

# DeepSeek API
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT=30

# 数据库配置
DATABASE_URL=sqlite:///data/reports.db
# 或 PostgreSQL
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# 向量库配置
VECTOR_MODEL=shibing624/text2vec-base-chinese
VECTOR_DIM=768
VECTOR_INDEX_PATH=data/vectors

# 爬虫配置
CRAWL_INTERVAL=3600
MAX_CONCURRENT=5
USER_AGENT=Mozilla/5.0 ...

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 监控与维护

#### 日志查看
```bash
# Docker 日志
docker logs -f research-ai

# 应用日志
tail -f logs/app.log
```

#### 数据备份
```bash
# 备份数据库
cp data/reports.db backup/reports_$(date +%Y%m%d).db

# 备份向量索引
tar -czf backup/vectors_$(date +%Y%m%d).tar.gz data/vectors/
```

#### 性能优化

1. **增加 worker 数量**：
   ```bash
   gunicorn -w 8 -b 0.0.0.0:5000 app:app
   ```

2. **启用 Redis 缓存**：
   ```env
   REDIS_URL=redis://localhost:6379/0
   ```

3. **优化向量索引**：
   - 使用 IVF 索引替代 Flat 索引
   - 定期重建索引

## 技术栈

### 后端框架
- **Flask 3.x** - 轻量级 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **Celery** - 分布式任务队列

### AI/ML
- **DeepSeek API** - 大语言模型（研报分析、内容提取）
- **sentence-transformers** - 文本向量化模型
- **FAISS** - 高效向量相似度搜索

### 数据处理
- **PyPDF2** - PDF 文件解析
- **BeautifulSoup4** - HTML 内容提取
- **Pandas** - 数据分析处理

### 前端
- **HTML5/CSS3** - 响应式界面
- **JavaScript** - 交互逻辑
- **ECharts** - 数据可视化图表

### 工具库
- **requests** - HTTP 客户端
- **python-dotenv** - 环境变量管理
- **APScheduler** - 定时任务调度
- **loguru** - 日志管理

### 部署
- **Docker** - 容器化部署
- **Gunicorn** - WSGI 服务器
- **Nginx** - 反向代理

## 常见问题

### Q1: 如何获取 DeepSeek API Key？

访问 [DeepSeek 官网](https://platform.deepseek.com/) 注册账号并创建 API Key。

### Q2: 向量索引占用内存过大怎么办？

可以调整向量维度或使用量化索引：
```python
# 在 config.py 中调整
VECTOR_DIM = 384  # 使用更小的维度
```

### Q3: 爬虫被网站封禁怎么办？

1. 增加请求间隔
2. 使用代理 IP 池
3. 随机 User-Agent

### Q4: 如何添加新的数据源？

在 `crawler/` 目录下创建新的爬虫类，继承 `BaseCrawler`：
```python
from crawler.base import BaseCrawler

class NewCrawler(BaseCrawler):
    def crawl(self, params):
        # 实现爬取逻辑
        pass
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页：[GitHub Repository]
- 问题反馈：[Issues]
- 邮箱：your-email@example.com

## 致谢

- [DeepSeek](https://platform.deepseek.com/) - 提供强大的 AI 能力
- [FAISS](https://github.com/facebookresearch/faiss) - 高效向量搜索
- [sentence-transformers](https://www.sbert.net/) - 文本向量化
- 所有贡献者和用户

---

**研报智库** - 让研报分析更智能、更高效
