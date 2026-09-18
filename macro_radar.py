import json
from datetime import datetime

data = {
    "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    "macro": {
        "usd_index": "待接入",
        "us10y": "待接入",
        "fed_expectation": "待接入"
    },

    "commodities": {
        "gold": "关注",
        "silver": "关注",
        "copper": "关注",
        "aluminum": "关注",
        "oil": "关注"
    },

    "events": {
        "nonfarm": "待接入",
        "cpi": "待接入",
        "fed_meeting": "待接入",
        "trump_statement": "待接入"
    },

    "analyst_watch": {
        "song_hongbing": "待整理",
        "eric_yeung": "待整理"
    }
}


with open(
    "/Users/lizhe/stock-radar/macro_radar.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("macro radar updated")
