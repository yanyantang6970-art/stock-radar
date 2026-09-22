"""只读健康检查；使用数据内时间，避免将本地提交时间冒充远端验证。"""
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent


def check(label, path, key):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        timestamp = data[key]
        age = (datetime.now() - datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).total_seconds()
        source = data.get('source_updated_at', timestamp)
        source_age = (datetime.now() - datetime.strptime(source, '%Y-%m-%d %H:%M:%S')).total_seconds()
        codes = {c[2:] if c[:2] in ('sz', 'sh', 'hk') else c for c in data['stocks']}
        expected = {'000426', '603993', '601600', '002202', '600598', '159587', '01378'}
        if codes != expected:
            state = '⚠️七股不完整'
        elif not (-60 <= age <= 900 and -60 <= source_age <= 900):
            state = '⚠️明显过期（非交易时段可正常停更）'
        else:
            state = '✅正常'
        print(f'{label}：{state}；更新时间 {timestamp}；行情来源 {source}')
    except FileNotFoundError:
        print(f'{label}：❌文件不存在')
    except Exception as exc:
        print(f'{label}：❌数据无法读取：{exc}')


if __name__ == '__main__':
    check('实时行情', Path('/Users/lizhe/radar.json'), 'updated_at')
    check('信号引擎', BASE / 'radar_v3.json', 'update_time')
    check('仓位引擎', BASE / 'position_signal.json', 'update_time')
