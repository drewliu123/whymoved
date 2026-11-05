import json
import zipfile
from pathlib import Path

root = Path(__file__).parent
verification = json.loads((root / 'verification.json').read_text())
parts = ['# 两版投研插件：完整原始产出\n', '统一问题：英伟达最近一个月跌了多少、为什么跌、业务发生了什么变化，接下来该关注什么？\n', '两轮分别检索并使用各自版本脚本执行；原文按原样拼接，未由协调方改写。独立检索带来的差别不能全部归因于版本。两轮登记于分开的试跑账本，不计入正式预测成绩。\n']
for v in ['0.1.1', '0.2.0']:
    home = root / ('run-' + v)
    status = verification['runs'][v]
    parts += ['\n---\n', '# ' + v + ' 原始报告\n', (home / 'memo.md').read_text(), '\n']
    parts += ['\n运行核验：' + str(status['claim_count']) + '条结论；' + str(status['hypothesis_count']) + '条假设；试跑归档ID ' + ', '.join(status['registered_memos']) + '。\n']
parts += ['\n---\n', '# 格式解释\n', (root / 'output-format.md').read_text()]
(root / 'both-outputs.md').write_text('\n'.join(parts))
with zipfile.ZipFile(root / 'research-outputs.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for filename in ['protocol.md','output-format.md','both-outputs.md','verification.json']:
        z.write(root / filename, filename)
    for v in ['0.1.1','0.2.0']:
        home = root / ('run-' + v)
        for filename in ['plan.json', 'claims.json', 'memo.json', 'memo.md', 'execution.json', 'forecast.json', 'red-team.json', 'redteam.json', 'forecast-input.json', 'forecaster-results.json', 'forecast-input-H1.json', 'forecaster-trials.json']:
            path = home / filename
            if path.is_file():
                z.write(path, str(Path('run-' + v) / filename))
        journal = home / 'journal'
        for path in journal.rglob('*'):
            if path.is_file() and path.suffix in {'.json', '.jsonl', '.md'}:
                z.write(path, str(Path('run-' + v) / path.relative_to(home)))
print('Created both-outputs.md and research-outputs.zip; only reports, ledgers, execution summaries and archives included.')
