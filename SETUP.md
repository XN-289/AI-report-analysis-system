# 部署指南

## 一、推送到 GitHub

### 1. 初始化本地仓库

```bash
cd "d:/有关研报的ai agent系统"
git init
git add .
git commit -m "Initial commit"
```

### 2. 创建远程仓库并推送

在 GitHub 上创建一个新仓库（例如 `research-report-ai-agent`），然后执行：

```bash
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git branch -M main
git push -u origin main
```

## 二、启用 GitHub Pages

1. 打开仓库页面，进入 **Settings** > **Pages**。
2. 在 **Source** 部分选择 **Deploy from a branch**。
3. **Branch** 选择 `main`，文件夹选择 `/docs`。
4. 点击 **Save**。
5. 等待几分钟后，站点将发布到 `https://<你的用户名>.github.io/<仓库名>/`。

> `docs/.nojekyll` 文件已就绪，确保 GitHub Pages 跳过 Jekyll 构建，直接提供静态文件。

## 三、自动化构建（可选）

如果项目包含构建步骤（如 `build.py`），可通过 GitHub Actions 实现自动化：

### 1. 创建工作流文件

在仓库中创建 `.github/workflows/deploy.yml`：

```yaml
name: Build and Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build static site
        run: python build.py

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 2. 启用 GitHub Actions

1. 进入仓库的 **Settings** > **Pages**。
2. 将 **Source** 改为 **GitHub Actions**。
3. 每次推送到 `main` 分支时，Actions 会自动构建并部署。

## 四、本地预览

```bash
# 如果使用 build.py 生成静态页面
python build.py

# 用 Python 启动本地服务器预览 docs/ 目录
cd docs
python -m http.server 8000
# 访问 http://localhost:8000
```
