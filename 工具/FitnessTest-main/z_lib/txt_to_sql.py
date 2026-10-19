#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将txt文件转换为MySQL插入命令的脚本
"""

import os
import sys
import re

def convert_time_format(value):
    """
    将时间格式 '3'20"' 转换为 '3分20秒'
    
    Args:
        value: 时间字符串
        
    Returns:
        str: 转换后的时间字符串
    """
    if "'" in value and '"' in value:
        # 分割分钟和秒数
        parts = value.split("'")
        if len(parts) == 2:
            minutes = parts[0].strip()
            seconds = parts[1].replace('"', '').strip()
            return f"{minutes}分{seconds}秒"
    return value

def add_unit_to_value(value, table_name):
    """
    根据表名为数值添加相应单位
    
    Args:
        value: 原始数值
        table_name: 表名
        
    Returns:
        str: 带单位的数值
    """
    # 定义各项目的单位
    units = {
        # 肺活量 - 毫升
        r'.*fei.*': '毫升',
        # 50米跑 - 秒
        r'.*50m.*': '秒',
        # 坐位体前屈 - 厘米
        r'.*zuowei.*': '厘米',
        # 跳绳 - 次
        r'.*tiaosheng.*': '次',
        # 跳远 - 厘米
        r'.*tiaoyuan.*': '厘米',
        # 仰卧起坐/引体向上 - 次
        r'.*(yangwo|yinti).*': '次',
        # 1000米/800米跑 - 时间格式已单独处理
        r'.*(1000m|800m).*': '',
        # 默认无单位
        r'.*': ''
    }
    
    # 查找匹配的单位
    for pattern, unit in units.items():
        if re.match(pattern, table_name.lower()):
            # 如果是时间类项目，已经处理过了
            if '分' in str(value) and '秒' in str(value):
                return str(value)
            # 其他项目添加单位
            elif unit and (str(value).replace('.', '').replace('-', '').isdigit() or (str(value).startswith('-') and str(value)[1:].replace('.', '').isdigit())):
                return f"{value}{unit}"
            else:
                return str(value)
    
    return str(value)

def get_columns_for_table(table_name):
    """
    根据表名返回对应的字段列表
    
    Args:
        table_name: 表名
        
    Returns:
        tuple: (字段列表, 字段数量)
    """
    # 定义不同表的字段结构
    table_configs = {
        # 跳绳类表：source + grade_1到grade_6
        r'.*tiaosheng.*': (['source'] + [f'grade_{i}' for i in range(1, 7)], 7),
        # 跳远类表：source + grade_7到grade_12  
        r'.*tiaoyuan.*': (['source'] + [f'grade_{i}' for i in range(7, 13)], 7),
        # 1000米和800米跑表：source + grade_5到grade_12
        r'.*(1000m|800m).*': (['source'] + [f'grade_{i}' for i in range(5, 13)], 9),
        # 仰卧起坐/引体向上类表：source + grade_3到grade_12
        r'.*(yangwo|yinti).*': (['source'] + [f'grade_{i}' for i in range(3, 13)], 11),
        # 默认表：source + grade_1到grade_12
        r'.*': (['source'] + [f'grade_{i}' for i in range(1, 13)], 13)
    }
    
    # 匹配表名
    for pattern, (columns, count) in table_configs.items():
        if re.match(pattern, table_name.lower()):
            return columns, count
    
    # 默认返回完整字段
    return ['source'] + [f'grade_{i}' for i in range(1, 13)], 13

def convert_txt_to_sql(input_file, output_file=None):
    """
    将txt文件转换为MySQL插入命令（支持多段数据和不同表结构）
    
    Args:
        input_file: 输入的txt文件路径
        output_file: 输出的sql文件路径（可选，默认为input_file.sql）
    """
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        return False
    
    if output_file is None:
        output_file = input_file.replace('.txt', '.sql')
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            print("错误: 文件为空")
            return False
        
        # 按照反斜杠分割不同的数据段
        segments = content.strip().split('\\')
        
        if not segments:
            print("错误: 没有找到有效的数据段")
            return False
        
        sql_lines = []
        sql_lines.append(f"-- 从 {input_file} 生成的SQL插入语句")
        sql_lines.append("-- 支持多段数据插入，用反斜杠连接")
        
        total_rows = 0
        
        for segment_idx, segment in enumerate(segments):
            lines = [line.strip() for line in segment.strip().split('\n') if line.strip()]
            
            if not lines:
                continue
            
            # 获取表名（第一行）
            table_name = lines[0].strip()
            
            # 根据表名获取字段配置
            columns, expected_fields = get_columns_for_table(table_name)
            columns_str = ", ".join(columns)
            
            # 构建插入语句
            sql_lines.append(f"INSERT INTO {table_name} ({columns_str}) VALUES")
            
            # 处理数据行
            data_rows = []
            for line in lines[1:]:  # 跳过第一行（表名）
                if line.strip():  # 跳过空行
                    values = line.strip().split()
                    if len(values) == expected_fields:  # 确保字段数量匹配
                        # 将数值用单引号包围（除了第一个source字段）
                        # 处理数值并添加单位
                        formatted_values = [values[0]]  # source字段保持原样
                        for val in values[1:]:
                            # 先处理时间格式转换
                            if '1000m' in table_name.lower() or '800m' in table_name.lower() or '1000' in table_name.lower() or '800' in table_name.lower():
                                processed_val = convert_time_format(val)
                            else:
                                processed_val = val
                            # 再添加单位
                            final_val = add_unit_to_value(processed_val, table_name)
                            formatted_values.append(f"'{final_val}'")
                        data_rows.append(f"({', '.join(formatted_values)})")
                    else:
                        print(f"警告: 行 '{line}' 的字段数量({len(values)}) 与表 {table_name} 期望的字段数量({expected_fields}) 不匹配")
            
            # 连接所有数据行
            if data_rows:
                sql_content = ',\n'.join(data_rows) + ';'
                sql_lines.append(sql_content)
                total_rows += len(data_rows)
            else:
                print(f"警告: 数据段 {segment_idx + 1} 没有找到有效的数据行")
        
        # 移除最后多余的分号
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))
        
        print(f"成功转换 {input_file} -> {output_file}")
        print(f"共处理 {len([s for s in segments if s.strip()])} 个数据段")
        print(f"共处理 {total_rows} 行数据")
        return True
            
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return False

def batch_convert(folder_path):
    """
    批量转换文件夹中的所有txt文件
    
    Args:
        folder_path: 文件夹路径
    """
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 {folder_path} 不存在")
        return
    
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"文件夹 {folder_path} 中没有找到txt文件")
        return
    
    print(f"找到 {len(txt_files)} 个txt文件")
    
    success_count = 0
    for txt_file in txt_files:
        input_path = os.path.join(folder_path, txt_file)
        if convert_txt_to_sql(input_path):
            success_count += 1
    
    print(f"\n转换完成: {success_count}/{len(txt_files)} 个文件成功转换")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python txt_to_sql.py <文件路径>           # 转换单个文件")
        print("  python txt_to_sql.py <文件夹路径> -batch  # 批量转换文件夹")
        return
    
    path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == '-batch':
        # 批量转换模式
        batch_convert(path)
    else:
        # 单文件转换模式
        convert_txt_to_sql(path)

if __name__ == "__main__":
    main()