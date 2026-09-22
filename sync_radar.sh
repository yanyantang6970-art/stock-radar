#!/bin/bash
set -e
cd "$HOME/stock-radar" || exit 1

cp "$HOME/radar.json" radar.json

git add -- radar.json

if ! git diff --cached --quiet -- radar.json; then
    git commit -m "auto update radar" -- radar.json
fi

# Generate locally before any network operation, even during an outage.
derived_ready=0
if /usr/bin/python3 "$HOME/stock-radar/derive_v35.py"; then
    derived_ready=1
fi

# Preserve primary upload priority, with bounded automatic retries.
primary_result=0
/usr/bin/python3 "$HOME/stock-radar/upload_v35.py" --main || primary_result=$?

if [ "$primary_result" -eq 0 ] && [ "$derived_ready" -eq 1 ]; then
    if ! /usr/bin/python3 "$HOME/stock-radar/upload_v35.py"; then
        echo "V3.5：上传失败，本地派生已完成，下次同步补推最新文件" >&2
    fi
fi
exit "$primary_result"
