"""在行情同步成功后，基于已提交的同一快照依次派生并发布 V3.5 文件。"""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

BASE = Path(__file__).resolve().parent
CODES = {'000426', '603993', '601600', '002202', '600598', '159587', '01378'}
OUTPUTS = ('radar_v3.json', 'position_signal.json')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=BASE, text=True, timeout=90)


def plain(code):
    return code[2:] if code[:2] in ('sz', 'sh', 'hk') else code


def main():
    with open(BASE / '.git/v35.lock', 'w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('V3.5：已有派生任务运行')
            return
        snapshot = git('show', 'HEAD:radar.json')
        radar = json.loads(snapshot)
        if {plain(c) for c in radar['stocks']} != CODES:
            raise ValueError('实时行情未包含完整七股')
        age = (datetime.now() - datetime.strptime(radar['updated_at'], '%Y-%m-%d %H:%M:%S')).total_seconds()
        if not -60 <= age <= 900:
            raise ValueError('实时行情明显过期，保留已有派生文件')
        with tempfile.TemporaryDirectory(prefix='v35-') as directory:
            temp = Path(directory)
            (temp / 'radar.json').write_text(snapshot, encoding='utf-8')
            for name in ('signal_engine.py', 'position_manager.py', 'stock_profile.json', 'macro_radar.json', 'position.json'):
                shutil.copy2(BASE / name, temp / name)
            for name in ('signal_engine.py', 'position_manager.py'):
                subprocess.run([sys.executable, name], cwd=temp, check=True, timeout=60)
            for name in OUTPUTS:
                data = json.loads((temp / name).read_text())
                if {plain(c) for c in data['stocks']} != CODES or data['source_updated_at'] != radar['updated_at']:
                    raise ValueError(name + '：七股或来源时间不匹配')
            for name in OUTPUTS:
                shutil.copyfile(temp / name, BASE / (name + '.tmp'))
                os.replace(BASE / (name + '.tmp'), BASE / name)
        if '--publish' in sys.argv:
            git('add', '--', *OUTPUTS)
            changed = subprocess.run(['git', 'diff', '--cached', '--quiet', '--', *OUTPUTS], cwd=BASE).returncode
            if changed == 1:
                git('commit', '-m', 'Update V3.5 derived radar signals', '--', *OUTPUTS)
            elif changed:
                raise RuntimeError('无法检查派生文件变更')
            git('push', 'origin', 'main')
        print('V3.5：七股派生完成，行情时间 ' + radar['updated_at'], flush=True)


if __name__ == '__main__':
    main()
