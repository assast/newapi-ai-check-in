FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖、cron 和浏览器所需的库
RUN apt-get update && apt-get install -y \
    curl \
    cron \
    # Camoufox 浏览器依赖
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libx11-xcb1 \
    libasound2 \
    libpci3 \
    # 虚拟显示服务器
    xvfb \
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
ENV DISPLAY=:99

# 创建日志目录
RUN mkdir -p /var/log

# 创建启动脚本
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# 启动虚拟显示服务器\n\
echo "🖥️ 启动虚拟显示服务器..."\n\
Xvfb :99 -screen 0 1280x720x24 > /dev/null 2>&1 &\n\
sleep 2\n\
echo "✅ 虚拟显示服务器已启动"\n\
\n\
# 检查并下载 Camoufox 浏览器\n\
echo "🔍 检查 Camoufox 浏览器..."\n\
if [ ! -d "$HOME/.local/share/camoufox" ]; then\n\
  echo "📥 首次运行，下载 Camoufox 浏览器..."\n\
  python3 -m camoufox fetch\n\
  echo "✅ Camoufox 浏览器下载完成"\n\
else\n\
  echo "✅ Camoufox 浏览器已存在"\n\
fi\n\
\n\
# 设置默认 cron 表达式（每 8 小时执行一次）\n\
CRON_SCHEDULE="${CRON_SCHEDULE:-0 */8 * * *}"\n\
\n\
echo "⏰ 设置定时任务: $CRON_SCHEDULE"\n\
\n\
# 创建 cron 任务文件\n\
echo "$CRON_SCHEDULE cd /app && DISPLAY=:99 /usr/local/bin/uv run main.py >> /var/log/checkin.log 2>&1" > /etc/cron.d/checkin\n\
\n\
# 设置权限\n\
chmod 0644 /etc/cron.d/checkin\n\
\n\
# 应用 cron 任务\n\
crontab /etc/cron.d/checkin\n\
\n\
# 立即执行一次（忽略退出码，避免容器重启）\n\
echo "🚀 立即执行一次签到..."\n\
cd /app && /usr/local/bin/uv run main.py || echo "⚠️ 首次签到完成（可能有失败）"\n\
\n\
# 启动 cron 服务\n\
echo "✅ 启动 cron 定时任务服务"\n\
echo "📋 日志文件: /var/log/checkin.log"\n\
cron -f\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
