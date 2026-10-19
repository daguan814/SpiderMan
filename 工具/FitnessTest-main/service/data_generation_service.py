"""
体测数据查询服务
根据性别、年级、分数查询对应的体测标准数据并返回JSON格式结果
"""

import json
import logging
import random
import re
from typing import Dict, List, Optional, Tuple
from db.db_to_cache import CACHE
from config.const import (
    PROJECT_MAPPING,
    GRADE_MAPPING,
    VALID_SCORES,
    HEIGHT_WEIGHT_STATS,
    GRADE_LIMITS,
    ZERO_SCORE_DATA,
    BMI_STANDARDS
)

# 配置日志
logger = logging.getLogger(__name__)


def _sample_truncated_normal(
    mean: float,
    std: float,
    min_value: float,
    max_value: float,
    max_attempts: int = 30
) -> float:
    """Sample from normal distribution constrained to [min_value, max_value]."""
    for _ in range(max_attempts):
        value = random.normalvariate(mean, std)
        if min_value <= value <= max_value:
            return value
    # Fallback to uniform within bounds to avoid boundary pile-ups.
    return random.uniform(min_value, max_value)


def get_display_name(project_name: str, grade: int) -> str:
    """获取项目显示名称

    Args:
        project_name: 项目名称
        grade: 年级 (1-12)

    Returns:
        str: 显示名称
    """
    if project_name == '仰卧起坐/引体向上':
        return '一分钟仰卧起坐' if grade <= 6 else '引体向上'
    if project_name == '仰卧起坐':
        return '一分钟仰卧起坐'
    elif project_name == '耐力跑':
        return '50米×8往返跑' if grade <= 6 else project_name
    return project_name


def generate_height_weight(gender: str, grade: int) -> Tuple[float, float]:
    """生成身高体重数据（正态分布随机偏移）

    Args:
        gender: 性别 ('男' 或 '女')
        grade: 年级 (1-12)

    Returns:
        Tuple[float, float]: (身高cm, 体重kg)
    """
    stats = HEIGHT_WEIGHT_STATS.get((gender, grade))
    if not stats:
        height_mean = 160.0 if gender == '男' else 155.0
        weight_mean = 50.0 if gender == '男' else 45.0
    else:
        height_mean = stats['height']
        weight_mean = stats['weight']

    height_std = height_mean * 0.07
    weight_std = weight_mean * 0.07

    limits = GRADE_LIMITS.get(grade, {'height': (150, 190), 'weight': (40, 75)})
    min_height, max_height = limits['height']
    min_weight, max_weight = limits['weight']

    height = _sample_truncated_normal(height_mean, height_std, min_height, max_height)
    weight = _sample_truncated_normal(weight_mean, weight_std, min_weight, max_weight)

    return round(height, 1), round(weight, 1)


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """计算BMI值

    Args:
        height_cm: 身高（厘米）
        weight_kg: 体重（千克）

    Returns:
        float: BMI值
    """
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 2)


def get_bmi_score(bmi: float, grade: int) -> int:
    """根据BMI值和年级获取BMI分数

    Args:
        bmi: BMI值
        grade: 年级

    Returns:
        int: BMI分数（100/80/60）
    """
    standards = BMI_STANDARDS.get(grade)
    if not standards:
        return 80

    normal_min, normal_max = standards['normal']
    if normal_min <= bmi <= normal_max:
        return 100

    if bmi <= standards['low']:
        return 80

    overweight_min, overweight_max = standards['overweight']
    if overweight_min <= bmi <= overweight_max:
        return 80

    if bmi > standards['obese']:
        return 60

    return 80


def calculate_total_score(results: Dict, gender: str, grade: int, bmi_score: int) -> float:
    """计算总分

    Args:
        results: 查询结果字典
        gender: 性别
        grade: 年级
        bmi_score: BMI分数

    Returns:
        float: 总分
    """
    weights = GRADE_WEIGHTS.get(grade, {})
    if not weights:
        return 0.0

    total = 0.0
    total += bmi_score * weights.get('BMI', 0)

    for project_key, weight in weights.items():
        if project_key == 'BMI':
            continue

    return round(total, 1)


def create_simple_response(data: Dict) -> str:
    """创建简单响应（仅返回数据，无嵌套结构）

    Args:
        data: 响应数据

    Returns:
        str: JSON格式的响应
    """
    return json.dumps(data, ensure_ascii=False, indent=2)


def create_error_response(message: str) -> str:
    """创建错误响应

    Args:
        message: 错误信息

    Returns:
        str: JSON格式的错误响应
    """
    return json.dumps({'错误': message}, ensure_ascii=False, indent=2)


def query_project_standard(
    table_name: str,
    grade_field: str,
    score: int,
    gender: str,
    grade: int,
    project_name: str
) -> Optional[str]:
    """从缓存中查询单个项目标准数据

    Args:
        table_name: 表名
        grade_field: 年级字段名
        score: 分数
        gender: 性别
        grade: 年级
        project_name: 项目名称

    Returns:
        Optional[str]: 查询结果值
    """
    try:
        value = CACHE.get_cached_value(table_name, grade_field, score)

        if value:
            display_name = get_display_name(project_name, grade)
            offset_projects = ['肺活量', '耐力跑', '一分钟跳绳', '50米×8往返跑', '50米跑']

            if display_name in offset_projects:
                if '分' in value:
                    parts = value.replace('分', ' ').replace('秒', '').split()
                    if len(parts) == 2:
                        minutes = int(parts[0])
                        seconds = int(parts[1])
                        total_seconds = minutes * 60 + seconds
                        offset = random.uniform(-0.05, 0.05)
                        new_total = int(total_seconds * (1 + offset))
                        new_minutes = new_total // 60
                        new_seconds = new_total % 60
                        value = f"{new_minutes}'{new_seconds:02d}"
                elif '秒' in value:
                    try:
                        num_value = float(value.replace('秒', ''))
                        offset = random.uniform(-0.05, 0.05)
                        new_value = num_value * (1 + offset)
                        if display_name == '肺活量':
                            value = str(int(round(new_value)))
                        else:
                            value = f"{new_value:.1f}"
                    except ValueError:
                        pass
                else:
                    try:
                        num_match = re.search(r'-?\d+\.?\d*', value)
                        if num_match:
                            num_value = float(num_match.group())
                            offset = random.uniform(-0.05, 0.05)
                            new_value = num_value * (1 + offset)
                            if display_name == '肺活量':
                                value = str(int(round(new_value)))
                            else:
                                value = f"{new_value:.2f}".rstrip('0').rstrip('.')
                    except (ValueError, AttributeError):
                        pass

            if "'" in value:
                return value

            num_match = re.search(r'-?\d+\.?\d*', value)
            if num_match:
                if display_name == '肺活量':
                    return str(int(round(float(num_match.group()))))
                return num_match.group()
            return value
        return None

    except Exception as e:
        logger.error(f"从缓存查询 {table_name} 错误: {e}")
        return None


def query_fitness_standards(gender: str, grade: int, score: int) -> str:
    """查询体测标准数据（使用缓存），包含BMI和总分计算

    Args:
        gender: 性别 (字符串'男'/'女' 或 整数 1/0)
        grade: 年级 (1-12)
        score: 分数

    Returns:
        str: JSON格式的查询结果（简单格式，无嵌套）
    """
    try:
        if not CACHE.is_initialized():
            return create_error_response("缓存未初始化，请先调用 CACHE.initialize_cache()")

        if isinstance(gender, int):
            gender = '男' if gender == 1 else '女' if gender == 0 else None
        if not gender or gender not in ['男', '女']:
            return create_error_response("性别参数无效")

        if grade not in range(1, 13):
            return create_error_response("年级参数无效")

        if score not in VALID_SCORES:
            return create_error_response(f"分数不符合标准，有效分数为: {', '.join(map(str, sorted(VALID_SCORES)))}")

        projects = PROJECT_MAPPING[gender]
        grade_field = GRADE_MAPPING[grade]
        height, weight = generate_height_weight(gender, grade)

        bmi = calculate_bmi(height, weight)

        results = {
            '身高': str(height),
            '体重': str(weight),
            'BMI': str(bmi),
            '800米跑': '',
            '1000米跑': '',
            '一分钟仰卧起坐': '',
            '引体向上': ''
        }

        for project_name, table_name in projects.items():
            value = query_project_standard(
                table_name, grade_field, score, gender, grade, project_name
            )
            if value:
                display_name = get_display_name(project_name, grade)
                if display_name == '耐力跑':
                    if gender == '男':
                        results['1000米跑'] = value
                    else:
                        results['800米跑'] = value
                else:
                    results[display_name] = value

        results['总分'] = str(score)

        return create_simple_response(results)

    except Exception as e:
        logger.error(f"查询错误: {e}")
        return create_error_response(f"服务器错误: {str(e)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== 初始化缓存 ===")
    if CACHE.initialize_cache():
        print("缓存初始化成功\n")
    else:
        print("缓存初始化失败\n")
        exit(1)

    print("=== 测试男生一年级(grade_1) 80分查询 ===")
    result = query_fitness_standards(1, 1, 80)
    print(result)

    print("\n=== 测试女生二年级(grade_2) 90分查询 ===")
    result = query_fitness_standards('女', 2, 90)
    print(result)
