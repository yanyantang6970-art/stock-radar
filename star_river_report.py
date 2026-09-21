import json
from datetime import datetime

RADAR_FILE = "radar.json"
V3_FILE = "radar_v3.json"
MACRO_FILE = "macro_radar.json"
OUTPUT_FILE = "star_river_daily_report.md"


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def macro_status(macro):
    commodities = macro.get("commodities", {})
    lines = []
    for k, name in [("gold", "黄金"), ("silver", "白银"), ("copper", "铜"), ("aluminum", "铝")]:
        if commodities.get(k):
            lines.append(f"- {name}：{commodities[k]}")
    return "\n".join(lines) or "- 暂无宏观商品数据"


def main():
    radar = load(RADAR_FILE)
    v3 = load(V3_FILE)
    macro = load(MACRO_FILE)

    stocks = v3.get("stocks", {})
    realtime = radar.get("stocks", {})

    rows = []
    focus = []
    risks = []

    for code, item in stocks.items():
        live = realtime.get(code, {})
        drivers = "、".join(item.get("drivers", item.get("reasons", [])))
        rows.append(
            f"|{item.get('name','')}|{live.get('price','')}|{live.get('change_pct','')}%|{item.get('score','')}|{item.get('signal','')}|{drivers}|"
        )
        focus.append((item.get("score", 0), item))

        if item.get("signal") == "REDUCE":
            risks.append(f"{item.get('name')}：风险评分偏高，需要关注")

    focus = sorted(focus, key=lambda x: x[0], reverse=True)[:3]

    report = f"""# 🌌 星河周期观测站

日期：{datetime.now().strftime('%Y-%m-%d')}  
更新时间：{radar.get('updated_at','未知')}

## 一、当前市场周期

贵金属周期：🟡观察  
工业金属：🟡观察  
市场风险：🟡中等

说明原因：

{macro_status(macro)}

## 二、7股雷达总览

| 股票 | 价格 | 涨跌 | 评分 | 信号 | 驱动 |
| -- | -- | -- | -- | -- | -- |
{chr(10).join(rows)}

## 三、重点关注

"""

    for score, item in focus:
        report += f"⭐ {item.get('name')}\n\n状态：{item.get('signal','')}\n\n原因：\n"
        for r in item.get("reasons", item.get("drivers", []))[:3]:
            report += f"- {r}\n"
        report += "\n"

    report += "## 四、风险提醒\n\n"
    report += "\n".join(risks) if risks else "当前暂无明显风险提示"

    report += "\n\n## 五、操作关注\n\n观察区：\n- 关注周期变化与评分变化\n\nT机会：\n- 关注短线波动与机动仓信号\n\n风险区：\n- 关注驱动因素转弱的股票\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print("🌌 星河日报生成完成")


if __name__ == "__main__":
    main()
