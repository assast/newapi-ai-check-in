FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install uv

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY . .

# 安装 Python 依赖
RUN uv sync --frozen

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🔍 检查 Camoufox 浏览器..."\n\
if [ ! -d "$HOME/.local/share/camoufox" ]; then\n\
  echo "📥 首次运行，下载 Camoufox 浏览器..."\n\
  python3 -m camoufox fetch\n\
  echo "✅ Camoufox 浏览器下载完成"\n\
else\n\
  echo "✅ Camoufox 浏览器已存在"\n\
fi\n\
echo "🚀 启动签到程序..."\n\
exec uv run main.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
