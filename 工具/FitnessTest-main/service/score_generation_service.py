import math
import random
from pathlib import Path
from typing import List, Dict
from config.const import SCORE_BUCKETS

BASE_DIR = Path(__file__).resolve().parents[1]
IO_DIR = BASE_DIR / 'IO'
GRADE_SEX_FILE = IO_DIR / 'grade_sex.txt'


def _read_people(file_path: Path) -> List[Dict]:
    # Read grade and sex from the people file
    people = []
    if not file_path.exists():
        raise FileNotFoundError(f'未找到文件: {file_path}')
    with file_path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                grade = int(parts[0])
            except ValueError:
                continue
            sex = parts[1]
            people.append({'grade': grade, 'sex': sex})
    return people


def _normalize_rate(rate: float) -> float:
    # Normalize rate into 0-1 range
    if rate < 0:
        raise ValueError('比例不能为负数')
    if rate > 1:
        return rate / 100.0
    return rate


def _allocate_counts(total: int, rates: Dict[str, float]) -> Dict[str, int]:
    # Allocate counts by rate and keep total exact
    # Largest remainder method to keep totals exact
    raw = {k: total * v for k, v in rates.items()}
    floors = {k: int(math.floor(v)) for k, v in raw.items()}
    remainder = total - sum(floors.values())
    if remainder > 0:
        order = sorted(raw.items(), key=lambda kv: (kv[1] - math.floor(kv[1])), reverse=True)
        for i in range(remainder):
            floors[order[i][0]] += 1
    return floors


def _generate_scores(people: List[Dict], excellent_rate: float, good_rate: float, pass_rate: float) -> List[Dict]:
    # Generate level and score for each person
    excellent_rate = _normalize_rate(excellent_rate)
    good_rate = _normalize_rate(good_rate)
    pass_rate = _normalize_rate(pass_rate)

    if pass_rate < excellent_rate + good_rate:
        raise ValueError('及格率必须包含优秀率和良好率（及格率 >= 优秀率 + 良好率）')
    if pass_rate > 1:
        raise ValueError('及格率不能超过 1 或 100%')

    pass_only_rate = pass_rate - excellent_rate - good_rate
    fail_rate = 1 - pass_rate

    rates = {
        '优秀': excellent_rate,
        '良好': good_rate,
        '及格': pass_only_rate,
        '不及格': fail_rate,
    }

    total = len(people)
    counts = _allocate_counts(total, rates)

    labels = []
    for level, count in counts.items():
        labels.extend([level] * count)
    random.shuffle(labels)

    results = []
    for i, person in enumerate(people):
        level = labels[i]
        score = random.choice(SCORE_BUCKETS[level])
        results.append({
            'index': i + 1,
            'grade': person['grade'],
            'sex': person['sex'],
            'level': level,
            'score': score,
        })
    return results


def _print_table(rows: List[Dict]):
    # Print results as a simple table
    headers = ['序号', '年级', '性别', '预估成绩', '等级']
    lines = []
    for r in rows:
        lines.append([
            str(r['index']),
            str(r['grade']),
            str(r['sex']),
            str(r['score']),
            str(r['level']),
        ])

    widths = [len(h) for h in headers]
    for row in lines:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells):
        return ' | '.join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(fmt_row(headers))
    print('-+-'.join('-' * w for w in widths))
    for row in lines:
        print(fmt_row(row))


def main():
    # CLI entry: read people and prompt for rates
    people = _read_people(GRADE_SEX_FILE)
    if not people:
        raise RuntimeError('未读取到任何年龄/性别数据')

    print(f'人数: {len(people)}')
    print('请输入比例（支持 0.1 或 10 表示 10%）')
    excellent_rate = float(input('优秀率: ').strip())
    good_rate = float(input('良好率: ').strip())
    pass_rate = float(input('及格率: ').strip())

    results = _generate_scores(people, excellent_rate, good_rate, pass_rate)
    _print_table(results)


if __name__ == '__main__':
    main()
