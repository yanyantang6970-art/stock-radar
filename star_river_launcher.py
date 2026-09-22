import os
import sys
import time
import subprocess
from datetime import datetime

# ============================================================
# 🌌 星河周期观测站 V3.3
# star_river_launcher.py
#
# 一键启动入口
# 不修改已有模块
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# 运行脚本
# ------------------------------------------------------------

def run_script(name):
    path = os.path.join(BASE_DIR, name)

    if not os.path.exists(path):
        return False

    subprocess.Popen(
        [sys.executable, path],
        cwd=BASE_DIR
    )

    return True


# ------------------------------------------------------------
# 检查进程
# ------------------------------------------------------------

def process_running(keyword):
    result = subprocess.run(
        ["pgrep", "-f", keyword],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return result.returncode == 0


# ------------------------------------------------------------
# 健康检查
# ------------------------------------------------------------

def health_check():
    check = os.path.join(BASE_DIR, "radar_health_check.py")

    if os.path.exists(check):
        subprocess.run(
            [sys.executable, check], cwd=BASE_DIR
        )


# ------------------------------------------------------------
# 最新数据时间
# ------------------------------------------------------------

def radar_time():
    radar = os.path.join(BASE_DIR, "radar.json")

    if not os.path.exists(radar):
        return "暂无数据"

    return datetime.fromtimestamp(
        os.path.getmtime(radar)
    ).strftime("%H:%M")


# ------------------------------------------------------------
# 主启动流程
# ------------------------------------------------------------

if __name__ == "__main__":

    print("🌌 星河周期观测站 V3.3 启动")
    print("=" * 40)

    print("\n执行健康检查...")
    health_check()

    print("\n检查行情采集...")

    if process_running("stock_radar.py"):
        print("行情采集：✅正常")
    else:
        run_script("stock_radar.py")
        print("行情采集：✅已启动")


    print("\n检查同步服务...")

    # Reuse the accepted sync entry; it runs signal then position in order.
    sync = subprocess.run(["/bin/bash", os.path.join(BASE_DIR, "sync_radar.sh")],
                          cwd=BASE_DIR)
    if sync.returncode != 0:
        print("同步服务：⚠️失败，请检查")
        sys.exit(sync.returncode)
    print("同步完成；信号引擎 → 仓位引擎已依次执行，状态如下：")
    health_check()

    print("\n最新数据：")
    print(radar_time())

    print("\n🌌 星河启动完成")
    print("=" * 40)
