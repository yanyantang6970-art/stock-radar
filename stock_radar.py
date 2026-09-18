import requests
import json
import time
import os
import sys
from datetime import datetime

# ============================================================
# 我的持仓实时雷达 V2
# 数据源：腾讯行情
# 只读取公开行情，不连接券商，不具备交易权限
# ============================================================

session = requests.Session()

# 国内行情不走系统代理
session.trust_env = False

# ------------------------------------------------------------
# 我的持仓
# 代码 : (名称, 持仓数量, 定位)
# ------------------------------------------------------------

stocks = {
    "sz000426": ("兴业银锡", 4500, "4000核心 + 500机动"),
    "sh603993": ("洛阳钼业", 6600, "观察仓"),
    "sh601600": ("中国铝业", 10300, "观察仓"),
    "sz002202": ("金风科技", 1000, "500观察 + 500机动"),
    "sh600598": ("北大荒", 1400, "农业个股"),
    "sz159587": ("粮食ETF", 10500, "农业Beta"),
    "hk01378": ("中国宏桥", 1500, "港股铝"),
}

# ------------------------------------------------------------
# 行情状态判断
# 以后我们还可以继续升级
# ------------------------------------------------------------

def market_state(change):
    if change >= 1.5:
        return "🟢 强"
    elif change >= -1.5:
        return "🟡 震荡"
    else:
        return "🔴 弱"


# ------------------------------------------------------------
# 获取腾讯实时行情
# ------------------------------------------------------------

def get_quotes():

    codes = ",".join(stocks.keys())

    url = f"https://qt.gtimg.cn/q={codes}"

    response = session.get(url, timeout=10)

    response.encoding = "gbk"

    return response.text


# ------------------------------------------------------------
# 解析行情
# ------------------------------------------------------------

def parse_quote(line):

    if '="' not in line:
        return None

    code = line.split('="')[0].replace("v_", "").strip()

    data = line.split('="')[1].rstrip('";').split("~")

    if len(data) < 35:
        return None

    try:

        name = data[1]

        current = float(data[3])

        yesterday = float(data[4])

        today_open = float(data[5])

        high = float(data[33])

        low = float(data[34])

        if yesterday == 0:
            change = 0
        else:
            change = (current - yesterday) / yesterday * 100

        return {
            "code": code,
            "name": name,
            "current": current,
            "change": change,
            "open": today_open,
            "high": high,
            "low": low,
        }

    except (ValueError, IndexError):
        return None


# ------------------------------------------------------------
# 主程序
# ------------------------------------------------------------

print()
print("=" * 72)
print("📡 我的持仓实时雷达 V2")
print("更新时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 72)

try:

    text = get_quotes()

    lines = text.strip().split(";")

    quotes = {}
    radar_data = {}

    for line in lines:

        quote = parse_quote(line)

        if quote:
            quotes[quote["code"]] = quote


    for code, info in stocks.items():

        my_name, position, role = info

        q = quotes.get(code)

        if q is None:

            print()
            print(f"{my_name}：⚠️ 暂未取得行情")
            continue


        state = market_state(q["change"])
        radar_data[code] = {"name": my_name, "position": position, "role": role, "price": q["current"], "change_pct": q["change"], "open": q["open"], "high": q["high"], "low": q["low"]}

        print()
        print(
            f"{my_name:<8} "
            f"现价:{q['current']:>8.3f}   "
            f"涨跌:{q['change']:>7.2f}%   "
            f"{state}"
        )

        print(
            f"          今开:{q['open']:>8.3f}   "
            f"最高:{q['high']:>8.3f}   "
            f"最低:{q['low']:>8.3f}"
        )

        print(
            f"          持仓:{position:<6}   "
            f"定位:{role}"
        )


    with open("/Users/lizhe/radar.json", "w", encoding="utf-8") as f:
            json.dump({"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "stocks": radar_data}, f, ensure_ascii=False, indent=2)
except Exception as e:

    print()
    print("❌ 行情读取失败")
    print("错误信息：", e)


print()
print("=" * 72)
print("提示：本程序只读取公开行情，不具备任何交易权限。")
print("=" * 72)
time.sleep(30)
os.execv(sys.executable, [sys.executable] + sys.argv)
