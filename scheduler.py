#!/usr/bin/env python3
"""
定时任务调度器
使用 schedule 库控制签到任务的执行频率
"""

import os
import sys
import time
import subprocess
import schedule
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)


def run_checkin():
    """执行签到任务"""
    print(f"\n{'='*60}")
    print(f"🕒 开始执行签到任务: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 导入并运行主程序
    try:
        # 使用 subprocess 运行，避免 sys.exit 影响调度器
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "main"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"⚠️ 签到任务返回非零退出码: {result.returncode}")
        
    except Exception as e:
        print(f"❌ 签到任务执行失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ 签到任务执行完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")


def parse_schedule_config(schedule_config: str) -> tuple[str, str]:
    """解析调度配置
    
    支持的格式:
    - "8h" 或 "8H" -> 每 8 小时
    - "30m" 或 "30M" -> 每 30 分钟
    - "09:00" -> 每天 09:00
    - "09:00,15:00,21:00" -> 每天 09:00, 15:00, 21:00
    
    Returns:
        (schedule_type, schedule_value)
        schedule_type: "hours", "minutes", "daily"
        schedule_value: 对应的值
    """
    schedule_config = schedule_config.strip()
    
    # 检查是否是时间格式（包含冒号）
    if ':' in schedule_config:
        return "daily", schedule_config
    
    # 检查是否是小时格式
    if schedule_config.lower().endswith('h'):
        hours = schedule_config[:-1].strip()
        try:
            int(hours)
            return "hours", hours
        except ValueError:
            raise ValueError(f"Invalid hours format: {schedule_config}")
    
    # 检查是否是分钟格式
    if schedule_config.lower().endswith('m'):
        minutes = schedule_config[:-1].strip()
        try:
            int(minutes)
            return "minutes", minutes
        except ValueError:
            raise ValueError(f"Invalid minutes format: {schedule_config}")
    
    raise ValueError(f"Invalid schedule format: {schedule_config}. Supported formats: '8h', '30m', '09:00', '09:00,15:00'")


def setup_schedule(schedule_config: str):
    """设置定时任务
    
    Args:
        schedule_config: 调度配置字符串
    """
    try:
        schedule_type, schedule_value = parse_schedule_config(schedule_config)
        
        if schedule_type == "hours":
            hours = int(schedule_value)
            schedule.every(hours).hours.do(run_checkin)
            print(f"⏰ 定时任务已设置: 每 {hours} 小时执行一次")
        
        elif schedule_type == "minutes":
            minutes = int(schedule_value)
            schedule.every(minutes).minutes.do(run_checkin)
            print(f"⏰ 定时任务已设置: 每 {minutes} 分钟执行一次")
        
        elif schedule_type == "daily":
            # 支持多个时间点，用逗号分隔
            times = [t.strip() for t in schedule_value.split(',')]
            for time_str in times:
                schedule.every().day.at(time_str).do(run_checkin)
                print(f"⏰ 定时任务已设置: 每天 {time_str} 执行")
        
    except ValueError as e:
        print(f"❌ 调度配置错误: {e}")
        print("使用默认配置: 每 8 小时执行一次")
        schedule.every(8).hours.do(run_checkin)


def main():
    """主函数"""
    print("🚀 newapi.ai 定时签到调度器启动")
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 获取调度配置
    schedule_config = os.getenv("SCHEDULE_TIME", "8h")
    print(f"📋 调度配置: {schedule_config}")
    
    # 设置定时任务
    setup_schedule(schedule_config)
    
    # 立即执行一次
    print("\n🚀 立即执行首次签到...\n")
    run_checkin()
    
    # 显示下次执行时间
    next_run = schedule.next_run()
    if next_run:
        print(f"\n⏰ 下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 开始循环调度
    print("\n✅ 调度器运行中，等待下次执行...\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n\n⚠️ 收到中断信号，调度器停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
