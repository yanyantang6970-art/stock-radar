#!/bin/bash
set -e
cd "$HOME/stock-radar" || exit 1

cp "$HOME/radar.json" radar.json

git add -- radar.json

if ! git diff --cached --quiet -- radar.json; then
    git commit -m "auto update radar" -- radar.json
fi

# Retry pending commits even when the data file has not changed.
git push origin main

# V3.5 runs only after the original radar push succeeds.
# A derived failure must not undo or block the completed radar sync.
if ! /usr/bin/python3 "$HOME/stock-radar/derive_v35.py" --publish; then
    echo "V3.5：派生或上传失败，下次同步重试" >&2
fi
