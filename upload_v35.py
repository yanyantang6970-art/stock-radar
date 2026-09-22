"""Bounded upload retries; local generation remains independent."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
OUTPUTS = ('radar_v3.json', 'position_signal.json')

def event(kind, **fields):
    record = dict(time=datetime.datetime.now().isoformat(timespec='seconds'), event=kind, **fields)
    with (BASE / '.git/v35-upload.jsonl').open('a') as stream:
        stream.write(json.dumps(record) + '\n')
    print(json.dumps(record), flush=True)

def run(*args, proxy=None):
    options = ['-c', 'http.proxy=' + proxy] if proxy else []
    return subprocess.run(['git', *options, *args], cwd=BASE, check=True, timeout=25,
                          env=dict(os.environ, GIT_TERMINAL_PROMPT='0'))

def main():
    primary = '--main' in sys.argv
    layer = 'radar' if primary else 'derived'
    configured = subprocess.run(['git', 'config', '--global', '--get', 'http.proxy'],
                                capture_output=True, text=True, timeout=5)
    fallback_proxy = configured.stdout.strip() if configured.returncode == 0 else None
    for attempt in range(1, 4):
        try:
            # Explicit, expiring fault injection only affects derived uploads.
            fault = BASE / '.git/v35-test-failure-until'
            if not primary and fault.exists() and time.time() < float(fault.read_text()):
                raise TimeoutError('simulated derived upload timeout')
            if not primary:
                run('add', '--', *OUTPUTS)
                changed = subprocess.run(['git', 'diff', '--cached', '--quiet', '--', *OUTPUTS], cwd=BASE).returncode
                if changed == 1:
                    run('commit', '-m', 'Update V3.5 derived radar signals', '--', *OUTPUTS)
                elif changed:
                    raise RuntimeError('Cannot inspect derived changes')
            run('push', 'origin', 'main', proxy=fallback_proxy if attempt > 1 else None)
            names = ('radar.json',) if primary else OUTPUTS
            event('upload_success', layer=layer, attempt=attempt,
                  timestamps={name: json.loads((BASE/name).read_text()).get('updated_at') or json.loads((BASE/name).read_text()).get('update_time') for name in names})
            return 0
        except (subprocess.SubprocessError, OSError, RuntimeError, ValueError) as exc:
            event('upload_failure', layer=layer, attempt=attempt, error=str(exc))
            if attempt < 3:
                time.sleep(5)
    return 1

if __name__ == '__main__':
    sys.exit(main())
