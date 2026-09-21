import os
import subprocess
from datetime import datetime

# ============================================================
# 🌌 星河周期观测站 V3.2
# radar_health_check.py
#
# 只检查状态，不修改任何交易/行情文件
# ============================================================

LOCAL_RADAR = "/Users/lizhe/radar.json"
REPO_PATH = "/Users/lizhe/stock-radar"


def check_process(keyword):
    try:
        result = subprocess.run(
            ["pgrep", "-f", keyword],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def local_radar_time():
    try:
        t = os.path.getmtime(LOCAL_RADAR)
        return datetime.fromtimestamp(t).strftime("%H:%M:%S")
    except Exception:
        return "无法读取"


def github_radar_time():
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=format:%H:%M:%S", "--", "radar.json"],
            cwd=REPO_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout.strip():
            return result.stdout.strip()
        return "无记录"
    except Exception:
        return "无法读取"


print("\n🌌 星河周期观测站 V3.2 状态检查")
print("=" * 40)

stock_ok = check_process("stock_radar")
sync_ok = check_process("sync_radar")

print("\n行情采集：")
print("✅正常" if stock_ok else "❌未启动")

print("\n同步服务：")
print("✅正常" if sync_ok else "❌未启动")

local_time = local_radar_time()
github_time = github_radar_time()

print("\n本地数据：")
print(local_time + " 更新")

print("\nGitHub：")
print(github_time + " 更新")

if local_time != "无法读取" and github_time != "无法读取":
    if local_time != github_time:
        print("\n问题：")
        print("本地数据与GitHub存在时间差")
        print("可能断点：sync_radar同步环节")
    else:
        print("\n状态：")
        print("本地与GitHub时间一致")

print("=" * 40)
