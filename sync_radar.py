import os
import time
import json
import subprocess
from datetime import datetime, time as dt_time

# ============================================================
# 🌌 星河周期观测站
# sync_radar.py
#
# 本地 radar.json -> GitHub radar.json 同步层
# 不修改 stock_radar.py
# ============================================================

LOCAL_RADAR = "/Users/lizhe/radar.json"
REPO_PATH = "/Users/lizhe/stock-radar"
SYNC_INTERVAL = 300  # 5分钟


# A股交易时间

def is_trade_time():
    now = datetime.now().time()

    morning = dt_time(9, 30) <= now <= dt_time(11, 30)
    afternoon = dt_time(13, 0) <= now <= dt_time(15, 0)

    return morning or afternoon


# 获取文件内容hash

def file_signature(path):
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return hash(f.read())


# 执行git命令

def git_run(command):
    return subprocess.run(
        command,
        cwd=REPO_PATH,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


# 同步一次

def sync():

    print("\n[{}] check radar.json".format(
        datetime.now().strftime("%H:%M:%S")
    ))

    result = git_run("git status --short radar.json")

    if not result.stdout.strip():
        print("no change")
        return

    print("radar.json detected update")

    git_run("git add radar.json")

    commit = git_run(
        'git commit -m "update radar data {}"'.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    if commit.returncode != 0:
        print("commit failed")
        print(commit.stderr)
        return

    print("commit created")

    push = git_run("git push")

    if push.returncode == 0:
        print("push success")
    else:
        print("push failed")
        print(push.stderr)


# 主循环

if __name__ == "__main__":

    print("🌌 radar sync service started")

    while True:

        try:
            if is_trade_time():
                sync()
            else:
                print(
                    "[{}] non trading time".format(
                        datetime.now().strftime("%H:%M:%S")
                    )
                )

        except Exception as e:
            print("sync error:", e)

        time.sleep(SYNC_INTERVAL)
