import json
from datetime import datetime

# ============================================================
# 🌌 星河周期观测站 V3.1
# 个股驱动因子评分引擎
# ============================================================

RADAR_FILE = "radar.json"
MACRO_FILE = "macro_radar.json"
PROFILE_FILE = "stock_profile.json"
OUTPUT_FILE = "radar_v3.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------
# 根据个股驱动因子匹配宏观主题
# ------------------------------------------------------------

def driver_score(profile, macro):
    score = 0
    reasons = []

    commodities = macro.get("commodities", {})
    labels = []

    mapping = {
        "silver": "silver",
        "gold": "gold",
        "copper": "copper",
        "aluminum": "aluminum",
        "agriculture": "agriculture",
        "food_security": "food_security"
    }

    for driver, weight in profile.get("drivers", {}).items():
        key = mapping.get(driver)
        if key and commodities.get(key) == "关注":
            score += int(weight * 20)
            reasons.append(f"{driver}周期支持")

    return score, reasons, profile.get("labels", [])


# ------------------------------------------------------------
# 股票评分
# ------------------------------------------------------------

def stock_score(stock, profile, macro):

    score = 50
    reasons = []

    change = stock.get("change_pct", 0)
    role = stock.get("role", "")

    if change >= 1.5:
        score += 15
        reasons.append("短线强势")
    elif change <= -1.5:
        score -= 15
        reasons.append("短线回调")
    else:
        reasons.append("震荡")

    driver_points, driver_reasons, labels = driver_score(profile, macro)

    score += driver_points
    reasons.extend(driver_reasons)

    if "核心" in role:
        score += 5
        reasons.append("核心仓")

    return max(0, min(100, score)), reasons, labels


# ------------------------------------------------------------
# 信号判断
# ------------------------------------------------------------

def generate_signal(score, change, role):

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


if __name__ == "__main__":

    radar = load_json(RADAR_FILE)
    macro = load_json(MACRO_FILE)
    profiles = load_json(PROFILE_FILE)

    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_updated_at": radar["updated_at"],
        "stocks": {}
    }

    for code, stock in radar.get("stocks", {}).items():

        profile = profiles.get(code, {"drivers": {}, "labels": []})

        score, reasons, labels = stock_score(
            stock,
            profile,
            macro
        )

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
            "drivers": labels,
            "reasons": reasons,
            "role": stock.get("role")
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("signal engine V3.1 completed")
