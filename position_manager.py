import json

POSITION_FILE = "position.json"
V3_FILE = "radar_v3.json"
RADAR_FILE = "radar.json"
OUTPUT_FILE = "position_signal.json"


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def translate_action(position, signal, reasons):
    core_action = "保持核心仓"
    t_action = {
        "type": "无机动仓动作",
        "amount": 0
    }

    t_amount = position.get("t_position", 0)

    if signal == "REDUCE":
        core_action = "核心仓减仓观察"

    if t_amount > 0:
        if signal == "T_BUY":
            t_action = {
                "type": "T_BUY_WATCH",
                "amount": t_amount
            }
        elif signal == "T_SELL":
            t_action = {
                "type": "T_SELL_WATCH",
                "amount": t_amount
            }

    return core_action, t_action


def main():
    position_data = load(POSITION_FILE).get("positions", {})
    v3 = load(V3_FILE).get("stocks", {})

    output = {"stocks": {}}

    for code, position in position_data.items():
        stock = v3.get(code, {})
        signal = stock.get("signal", "HOLD")
        reasons = stock.get("reasons", stock.get("drivers", []))

        core_action, t_action = translate_action(
            position,
            signal,
            reasons
        )

        output["stocks"][code] = {
            "name": position.get("name"),
            "total": position.get("total"),
            "core": position.get("core"),
            "t_position": position.get("t_position"),
            "signal": signal,
            "core_action": core_action,
            "t_action": t_action,
            "reason": reasons
        }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("🌌 position signal generated")


if __name__ == "__main__":
    main()
