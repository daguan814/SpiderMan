"""
Fitness data generation runner.
"""

import json
import csv
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional
from service.score_generation_service import _read_people, _generate_scores
from service.data_generation_service import query_fitness_standards
from db.db_to_cache import CACHE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
IO_DIR = BASE_DIR / 'IO'
GRADE_SEX_FILE = IO_DIR / 'grade_sex.txt'


def generate_batch_fitness_data(
        people: List[Dict],
        excellent_rate: float,
        good_rate: float,
        pass_rate: float
) -> List[Dict]:
    # Generate complete fitness data in batch
    if not CACHE.is_initialized():
        logger.info("缓存未初始化，正在初始化...")
        if not CACHE.initialize_cache():
            raise RuntimeError("缓存初始化失败")

    logger.info(f"正在为 {len(people)} 人生成分数...")
    score_results = _generate_scores(people, excellent_rate, good_rate, pass_rate)

    logger.info("正在生成完整的体测数据...")
    fitness_data_list = []

    for i, score_result in enumerate(score_results, 1):
        grade = score_result['grade']
        sex = score_result['sex']
        score = score_result['score']
        level = score_result['level']

        fitness_json = query_fitness_standards(sex, grade, score)
        fitness_data = json.loads(fitness_json)

        result = {
            '序号': i,
            '年级': grade,
            '性别': sex,
            '等级': level,
            '分数': score
        }

        if '错误' not in fitness_data:
            result.update(fitness_data)
        else:
            logger.warning(f"第 {i} 人生成数据失败: {fitness_data['错误']}")
            result['错误'] = fitness_data['错误']

        fitness_data_list.append(result)

        if i % 10 == 0:
            logger.info(f"已生成 {i}/{len(people)} 条数据")

    logger.info(f"完成！共生成 {len(fitness_data_list)} 条体测数据")
    return fitness_data_list


def generate_from_file(
        file_path: Optional[Path] = None,
        excellent_rate: float = 0.3,
        good_rate: float = 0.5,
        pass_rate: float = 0.9
) -> List[Dict]:
    # Read people data from a file and generate fitness data
    if file_path is None:
        file_path = GRADE_SEX_FILE

    logger.info(f"正在从文件读取人员信息: {file_path}")
    people = _read_people(file_path)

    if not people:
        raise ValueError(f"未从文件 {file_path} 中读取到任何人员信息")

    logger.info(f"读取到 {len(people)} 人的信息")
    return generate_batch_fitness_data(people, excellent_rate, good_rate, pass_rate)


def save_to_csv(data: List[Dict], output_path: Path) -> None:
    # Write rows to CSV using keys from the first record
    if not data:
        logger.warning("No data to write")
        return

    headers = list(data[0].keys())
    with output_path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, '') for k in headers})

    logger.info(f"CSV saved to: {output_path}")


def print_summary(data: List[Dict]):
    # Print a summary of generated data
    if not data:
        print("没有数据")
        return

    print("\n" + "=" * 60)
    print("数据摘要统计")
    print("=" * 60)

    level_counts = {}
    for row in data:
        level = row.get('等级', '未知')
        level_counts[level] = level_counts.get(level, 0) + 1

    print(f"\n总人数: {len(data)}")
    print("\n等级分布:")
    for level in ['优秀', '良好', '及格', '不及格']:
        count = level_counts.get(level, 0)
        percentage = count / len(data) * 100
        print(f"  {level}: {count} 人 ({percentage:.1f}%)")
    pass_count = (
        level_counts.get('优秀', 0)
        + level_counts.get('良好', 0)
        + level_counts.get('及格', 0)
    )
    pass_rate = pass_count / len(data) * 100
    print(f"  合格率(优秀+良好+及格): {pass_rate:.1f}%")

    grade_counts = {}
    for row in data:
        grade = row.get('年级', 0)
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    print("\n年级分布:")
    for grade in sorted(grade_counts.keys()):
        count = grade_counts[grade]
        print(f"  {grade} 年级: {count} 人")

    sex_counts = {}
    for row in data:
        sex = row.get('性别', '未知')
        sex_counts[sex] = sex_counts.get(sex, 0) + 1

    print("\n性别分布:")
    for sex, count in sex_counts.items():
        print(f"  {sex}: {count} 人")

    total_scores = [float(row.get('总分', 0)) for row in data if '总分' in row]
    if total_scores:
        avg_score = sum(total_scores) / len(total_scores)
        max_score = max(total_scores)
        min_score = min(total_scores)
        print("\n总分统计:")
        print(f"  平均分: {avg_score:.1f}")
        print(f"  最高分: {max_score:.1f}")
        print(f"  最低分: {min_score:.1f}")

    print("=" * 60 + "\n")


def auto_generate_workflow(
        excellent_rate: float = 0.3,
        good_rate: float = 0.5,
        pass_rate: float = 0.9
) -> List[Dict]:
    # Run the full flow: read -> generate -> print summary
    logger.info("开始自动化体测数据生成流程")
    logger.info(
        f"配置: 优秀率 {excellent_rate * 100 if excellent_rate <= 1 else excellent_rate}%, "
        f"良好率 {good_rate * 100 if good_rate <= 1 else good_rate}%, "
        f"及格率 {pass_rate * 100 if pass_rate <= 1 else pass_rate}%"
    )

    data = generate_from_file(
        excellent_rate=excellent_rate,
        good_rate=good_rate,
        pass_rate=pass_rate
    )

    print_summary(data)
    csv_path = IO_DIR / 'fitness_data.csv'
    save_to_csv(data, csv_path)
    logger.info("自动化流程完成！")
    return data


if __name__ == "__main__":
    print("=" * 60)
    print("体测数据自动生成系统")
    print("=" * 60)

    data = auto_generate_workflow(
        excellent_rate=0.1,
        good_rate=0.3,
        pass_rate=0.9
    )

    sample_count = min(5, len(data))
    if sample_count:
        print(f"\n随机抽样 {sample_count} 条数据预览:")
        print(json.dumps(random.sample(data, sample_count), ensure_ascii=False, indent=2))
