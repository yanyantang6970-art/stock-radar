import json
from datetime import datetime

# ============================================================
# 🌌 星河周期观测站 V3
# signal_engine.py
#
# 读取:
#   radar.json          股票实时数据
#   macro_radar.json    宏观周期数据
#
# 输出:
#   BUY / HOLD / T_BUY / T_SELL / REDUCE
# ============================================================

RADAR_FILE = "radar.json"
MACRO_FILE = "macro_radar.json"
OUTPUT_FILE = "radar_v3.json"


# ------------------------------------------------------------
# 读取数据
# ------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# 宏观评分
# ------------------------------------------------------------

def macro_score(macro):
    score = 0
    reasons = []

    commodities = macro.get("commodities", {})

    for key in ["gold", "silver", "copper", "aluminum"]:
        if commodities.get(key) == "关注":
            score += 5
            reasons.append(f"{key}周期关注")

    return score, reasons


# ------------------------------------------------------------
# 个股评分
# ------------------------------------------------------------

def stock_score(stock, macro_points):

    score = 50
    reasons = []

    change = stock.get("change_pct", 0)
    role = stock.get("role", "")

    # 当日强弱
    if change >= 1.5:
        score += 15
        reasons.append("短线强势")
    elif change <= -1.5:
        score -= 15
        reasons.append("短线回调")
    else:
        reasons.append("震荡")

    # 宏观支持
    score += macro_points

    if macro_points > 0:
        reasons.append("宏观周期支持")

    # 核心仓保护
    if "核心" in role:
        score += 5
        reasons.append("核心仓")

    return max(0, min(100, score)), reasons


# ------------------------------------------------------------
# 信号判断
# ------------------------------------------------------------

def generate_signal(score, change, role):

    # 做T优先
    if "机动" in role and change >= 2:
        return "T_SELL"

    if "机动" in role and change <= -2:
        return "T_BUY"

    if score >= 80:
        return "BUY"

    if score >= 60:
        return "HOLD"

    if score < 40:
        return "REDUCE"

    return "HOLD"


# ------------------------------------------------------------
# 主程序
# ------------------------------------------------------------

if __name__ == "__main__":

    radar = load_json(RADAR_FILE)
    macro = load_json(MACRO_FILE)

    macro_points, macro_reason = macro_score(macro)

    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "macro_score": macro_points,
        "stocks": {}
    }

    for code, stock in radar.get("stocks", {}).items():

        score, reasons = stock_score(stock, macro_points)

        signal = generate_signal(
            score,
            stock.get("change_pct", 0),
            stock.get("role", "")
        )

        result["stocks"][code] = {
            "name": stock.get("name"),
            "price": stock.get("price"),
            "score": score,
            "signal": signal,
            "reasons": reasons + macro_reason,
            "role": stock.get("role")
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("signal engine completed")
