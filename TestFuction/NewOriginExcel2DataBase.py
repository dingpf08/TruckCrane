"""
原始Excel转数据库格式工具

用途：
    本工具用于将建筑起重机（如汽车吊）工况的原始Excel数据批量转换为适合数据库存储和分析的标准行式数据。
    - 支持批量选择多个Excel文件（主臂工况和主臂+副臂工况均可）。
    - 自动识别文件名中的关键信息（如型号、工况编号、工况名称）。
    - 将原始的二维交叉表（主臂长×幅度或仰角）转换为一行一条记录的数据库友好格式。
    - 输出为新的Excel文件，便于后续数据库导入或数据分析。

【输入文件格式】
1. 文件名格式（必须严格遵循以下格式之一）：
    A. 主臂工况文件：
        格式：工况编号-(汽车吊型号)-(工况名称).xlsx
        示例：1-(STC250E-1)-(配重6.2t，支腿全伸).xlsx
            1：工况编号
            STC250E-1：汽车吊型号
            配重6.2t，支腿全伸：工况名称
    B. 主臂+副臂工况文件：
        格式：(汽车吊型号)-(主臂+副臂工况名称).xlsx
        示例：(STC250E-1)-(配重30t,主臂50.5).xlsx
            STC250E-1：汽车吊型号
            配重30t,主臂50.5：主臂+副臂工况名称
    注：文件名格式不正确会导致程序无法识别和处理。

2. 文件内容格式：
    A. 主臂工况文件内容：
        - 第一行（第1行，第2列及以后）：主臂长度（单位：米），如 28, 31, 34, ...
        - 第一列（第2行及以后，第1列）：幅度（单位：米），如 10, 12, 14, ...
        - 交叉单元格：对应主臂长度和幅度下的额定吊重（单位：吨），如 6.2, 5.8, ...
        示例：
            |   | 28 | 31 | 34 |
            |---|----|----|----|
            | 10|6.2 |5.8 |5.5 |
            | 12|5.9 |5.5 |5.2 |
            | 14|5.5 |5.2 |4.9 |
    B. 主臂+副臂工况文件内容：
        一张表有两个不同长度副臂工况的额定起重量，前四列为第一种工况的额定起重量，后四列为第二种工况的额定起重量
        - 第一行第二列（合并了3列单元格）和第一行第三列（合并了3列单元格）分别为不同的主臂+副臂工况名称：主臂长度1(m)+副臂长度1(m)，主臂长度(m)+副臂长度(m)
        -第二行第二列开始，每三列是对应主臂+副臂工况下的工作幅度，即第二行第二列、第二行第三列，第二行第四列为主工况"臂长度1(m)+副臂长度1(m)"对应的工作幅度；第二行第五列、第二行第六列，第二行第七列为主工况"臂长度1(m)+副臂长度1(m)"对应的工作幅度，
        -
        -第一列（第3行及以后）：为主臂长度1(m)+副臂长度1(m)对应的 仰角（单位：度），如 80, 78, 76, ...
        -第八列（第3行及以后）：主为主臂长度2(m)+副臂长度2(m)对应的 仰角（单位：度），如 80, 78, 76, ...

【输出文件格式】
1. 输出文件名：
    - 格式：汽车吊名称-额定起重量表-时间戳.xlsx
      例如：STC250E-1-额定起重量表-20240601_153000.xlsx
    - 保存位置：默认保存在第一个输入文件的同一目录下。
2. 输出文件内容：
    - 每一行为一条数据库格式的记录，包含以下字段（列）：
        TruckCraneID                汽车吊型号
        ConditionID                 工况编号
        SpeWorkCondition            工况名称
        TruckCraneRange             幅度
        TruckCraneMainArmLen        主臂长
        TruckCraneRatedLiftingCap   额定吊重
        IsJibHosCon                 是否副臂工况（"是"/"否"）
        SecondSpeWorkCondition      副臂工况名称
        SecondElevation             仰角
        SecondMainArmLen            副臂主臂长
        SecondTruckCraneRatedLiftingCap 副臂额定吊重
    - 主臂工况：IsJibHosCon为"否"，副臂相关字段为空或0。
    - 如果有主臂+副臂工况：IsJibHosCon修改为"是"，在主臂工况后面的副臂相关字段填充对应数据。
    - 排序规则：
        1. 汽车吊型号（TruckCraneID）
        2. 工况编号（ConditionID）
        3. 工况名称（SpeWorkCondition）
        4. 主臂长（TruckCraneMainArmLen）
        5. 幅度（TruckCraneRange）
        6. 额定吊重（TruckCraneRatedLiftingCap）

【使用流程】
1. 运行脚本，弹出文件选择窗口，选择要处理的Excel文件（可多选）。
2. 程序自动识别文件类型、读取内容、转换格式。
3. 转换完成后，输出新Excel文件到输入文件目录，并弹窗提示处理结果和统计信息。
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

# 定义最终输出的所有列
ALL_REQUIRED_COLUMNS = [
    'TruckCraneID', 'ConditionID', 'SpeWorkCondition', 
    'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap',
    'IsJibHosCon', 'SecondSpeWorkCondition', 'SecondElevation',
    'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap'
]

def extract_info_from_filename(filename):
    """
    从文件名中提取信息，可以处理两种格式的文件名：
    1. 主臂吊装工况: 工况编号-(汽车吊型号)-(工况名称).xlsx
    2. 主臂+副臂吊装工况: (汽车吊型号)-(主臂+副臂工况名称).xlsx
    
    Args:
        filename (str): 文件名
        
    Returns:
        tuple: (汽车吊型号, 工况编号, 工况名称, 是否为副臂工况, 副臂工况名称)
               对于主臂工况，副臂工况名称为None
               对于副臂工况，工况编号和工况名称为None
    """
    try:
        # 提取文件名 (不含扩展名)
        base_name = os.path.splitext(os.path.basename(filename))[0]
        
        # 从文件名模式识别格式
        main_pattern = r'^(\d+)-\((.+?)\)-\((.+?)\)'
        jib_pattern = r'^\((.+?)\)-\((.+?)\)'
        
        # 尝试匹配主臂吊装工况格式
        main_match = re.match(main_pattern, base_name)
        if main_match:
            condition_id = int(main_match.group(1))
            truck_crane_id = main_match.group(2)
            work_condition = main_match.group(3)
            return truck_crane_id, condition_id, work_condition, False, None
        
        # 尝试匹配主臂+副臂吊装工况格式
        jib_match = re.match(jib_pattern, base_name)
        if jib_match:
            truck_crane_id = jib_match.group(1)
            jib_condition = jib_match.group(2)
            return truck_crane_id, None, None, True, jib_condition
        
        # 如果都不匹配，抛出错误
        raise ValueError(f"文件名 '{base_name}' 不符合要求的格式")
        
    except Exception as e:
        raise ValueError(f"处理文件名 '{filename}' 时出错: {str(e)}")

def process_main_excel_file(file_path):
    """
    处理主臂Excel文件，将交叉表转换为数据库格式
    主臂工况：行=幅度，列=主臂长，数据区=额定吊重
    
    Args:
        file_path (str): Excel文件路径
    Returns:
        DataFrame: 转换后的数据库格式数据
    Raises:
        ValueError: 如果文件处理失败或未提取到有效数据
    """
    try:
        print(f"  - 开始读取主臂文件: {file_path}")
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        if df.empty:
            raise ValueError("Excel文件不包含数据")
        print(f"  - 主臂表格尺寸: {df.shape[0]}行 x {df.shape[1]}列")
        if df.shape[0] < 2 or df.shape[1] < 2:
            raise ValueError("Excel表格至少需要2行2列")

        # 从文件名提取信息
        file_name = os.path.basename(file_path)
        truck_crane_id, condition_id, work_condition, _, _ = extract_info_from_filename(file_name)

        # 获取幅度（行索引，从第2行开始，第1列）
        ranges = df.iloc[1:, 0].values
        # 获取主臂长（列索引，第1行，从第2列开始）
        arm_lengths = df.iloc[0, 1:].values

        # 数据清理和提取
        results = []
        
        clean_ranges = []
        for i, val in enumerate(ranges):
            try:
                if pd.isna(val): continue
                clean_val = float(str(val).strip())
                clean_ranges.append((i, clean_val))
            except ValueError:
                print(f"Warning: 无法解析幅度值 '{val}' 在行 {i+2}: 跳过.")

        clean_arm_lengths = []
        for j, val in enumerate(arm_lengths):
            try:
                if pd.isna(val): continue
                clean_val = float(str(val).strip())
                clean_arm_lengths.append((j, clean_val))
            except ValueError:
                print(f"Warning: 无法解析主臂长值 '{val}' 在列 {j+2}: 跳过.")

        if not clean_ranges or not clean_arm_lengths:
            raise ValueError("未能提取到有效的幅度或主臂长数据")

        for i, range_val in clean_ranges:
            for j, arm_len in clean_arm_lengths:
                try:
                    lifting_cap = df.iloc[i+1, j+1]
                    if pd.isna(lifting_cap) or (isinstance(lifting_cap, str) and not str(lifting_cap).strip()):
                        continue # 跳过空值或只有空白字符串的单元格

                    try:
                        lifting_cap_val = float(str(lifting_cap).strip())
                    except ValueError:
                        print(f"Warning: 无法将值 '{lifting_cap}' 转换为数字，跳过 (行={i+2}, 列={j+2})")
                        continue
                    
                    if lifting_cap_val <= 0: continue # 跳过小于等于0的吊重

                    results.append({
                        'TruckCraneID': truck_crane_id,
                        'ConditionID': condition_id,
                        'SpeWorkCondition': work_condition,
                        'TruckCraneRange': range_val,
                        'TruckCraneMainArmLen': arm_len,
                        'TruckCraneRatedLiftingCap': lifting_cap_val,
                        'IsJibHosCon': "否",
                        'SecondSpeWorkCondition': "",
                        'SecondElevation': 0.0,
                        'SecondMainArmLen': 0.0,
                        'SecondTruckCraneRatedLiftingCap': 0.0
                    })
                except Exception as e:
                    print(f"Warning: 处理主臂数据时出错 (行={i+2}, 列={j+2}): {str(e)}")
                    continue

        result_df = pd.DataFrame(results, columns=ALL_REQUIRED_COLUMNS)
        
        if result_df.empty:
            raise ValueError("无法从Excel提取有效主臂数据")

        # 确保主臂相关的数值列是数值类型
        for col in ['ConditionID', 'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap']:
            if col in result_df.columns:
                result_df[col] = pd.to_numeric(result_df[col], errors='coerce')

        # 确保副臂相关的数值列是数值类型，并填充默认值0
        for col in ['SecondElevation', 'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap']:
            if col in result_df.columns:
                result_df[col] = pd.to_numeric(result_df[col], errors='coerce').fillna(0.0)

        # 确保字符串列填充默认值""
        for col in ['SpeWorkCondition', 'IsJibHosCon', 'SecondSpeWorkCondition']:
            if col in result_df.columns:
                result_df[col] = result_df[col].astype(str).replace('nan', '').replace('None', '').fillna('')
        result_df['IsJibHosCon'] = "否"

        return result_df

    except Exception as e:
        # 打印更详细的错误信息，包括文件名和错误内容
        print(f"Error processing main arm file {os.path.basename(file_path)}: {e}")
        # 捕获并重新抛出更明确的错误
        raise ValueError(f"处理主臂文件 '{os.path.basename(file_path)}' 时出错: {str(e)}")

def process_jib_excel_file(file_path):
    """
    处理主臂+副臂Excel文件，将特定布局的交叉表转换为数据库格式。
    一张表有两个不同长度副臂工况的额定起重量。
    - 第一行: 两个副臂工况的名称 (合并单元格)
    - 第二行: 幅度 (每三个单元格一组)
    - 第一列 (从第3行起): 第一个工况的仰角
    - 第八列 (从第3行起): 第二个工况的仰角
    - 交叉单元格: 额定吊重
    
    Args:
        file_path (str): Excel文件路径
    Returns:
        DataFrame: 转换后的数据库格式数据
    Raises:
        ValueError: 如果文件处理失败或未提取到有效数据
    """
    try:
        print(f"  - 开始读取主臂+副臂文件: {file_path}")
        # 使用header=None读取，保留原始结构以便处理合并单元格（虽然pandas读取后合并信息会丢失，但我们可以根据固定位置解析）
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        
        if df.empty:
            raise ValueError("Excel文件不包含数据")
        print(f"  - 副臂表格尺寸: {df.shape[0]}行 x {df.shape[1]}列")
        
        # 提取文件名中的基本信息
        file_name = os.path.basename(file_path)
        truck_crane_id, _, _, _, jib_condition_from_filename = extract_info_from_filename(file_name)
        
        results = []
        
        # --- 处理第一个副臂工况 ---
        # 尝试从第一行第二列（索引1）获取第一个工况名称
        # 从文件内容第一行获取具体工况名称，如果为空则使用文件名中的副臂工况名称作为 fallback
        jib_content_condition_1 = df.iloc[0, 1] if df.shape[1] > 1 and pd.notna(df.iloc[0, 1]) else ""
        if not isinstance(jib_content_condition_1, str): # Ensure it's a string
            jib_content_condition_1 = str(jib_content_condition_1)
        jib_content_condition_1 = jib_content_condition_1.strip()
        
        # 构建最终的 SecondSpeWorkCondition
        final_second_spe_work_condition_1 = jib_condition_from_filename
        if jib_content_condition_1:
            final_second_spe_work_condition_1 = f"{final_second_spe_work_condition_1}, {jib_content_condition_1}"
        elif not final_second_spe_work_condition_1: # If both are empty, use a default
            final_second_spe_work_condition_1 = "未知副臂工况"

        print(f"  - 识别到第一个副臂工况名称 (文件内容): '{jib_content_condition_1}', 最终输出: '{final_second_spe_work_condition_1}'")
        
        # 第一个工况的仰角在第一列 (索引 0), 从第3行 (索引 2) 开始
        elevations_1 = df.iloc[2:, 0].values
        # 第一个工况的幅度在第二行 (索引 1), 列索引 1, 2, 3
        ranges_1_cols = [1, 2, 3]
        # 第一个工况的数据列是 2, 3, 4 (索引 1, 2, 3)
        data_cols_1 = [1, 2, 3]
        
        # 提取幅度值
        ranges_1_values = [df.iloc[1, col] for col in ranges_1_cols if df.shape[1] > col and pd.notna(df.iloc[1, col])]
        print(f"  - 第一个工况幅度值: {ranges_1_values}")

        # 循环处理第一个工况的数据
        for i, elevation in enumerate(elevations_1):
            if pd.isna(elevation) or (isinstance(elevation, str) and not elevation.strip()): continue
            try:
                 elevation_val = float(str(elevation).strip())
            except ValueError:
                 print(f"Warning: 无法解析第一个工况仰角值 '{elevation}' 在行 {i+3}, 跳过.")
                 continue

            # 遍历对应的数据列提取吊重
            for j, data_col in enumerate(data_cols_1):
                if df.shape[1] <= data_col: continue # 避免列越界
                lifting_cap = df.iloc[i+2, data_col]

                if pd.isna(lifting_cap) or (isinstance(lifting_cap, str) and not str(lifting_cap).strip()):
                    continue # 跳过空值或只有空白字符串的单元格
                
                try:
                    lifting_cap_val = float(str(lifting_cap).strip())
                except ValueError:
                     print(f"Warning: 无法解析第一个工况额定吊重值 '{lifting_cap}' 在行 {i+3}, 列 {data_col+1}, 跳过.")
                     continue

                if lifting_cap_val <= 0: continue # 跳过小于等于0的吊重

                # 查找当前列对应的幅度值
                current_range = None
                if j < len(ranges_1_values): # 使用索引 j 来对应幅度值列表
                     current_range = ranges_1_values[j]
                
                if current_range is None or (isinstance(current_range, str) and not str(current_range).strip()):
                     print(f"Warning: 第一个工况在列 {data_col+1} 未找到对应幅度值，跳过数据 (仰角={elevation_val}, 吊重={lifting_cap_val}).")
                     continue

                try:
                     range_val = float(str(current_range).strip())
                except ValueError:
                     print(f"Warning: 无法解析第一个工况幅度值 '{current_range}' 在列 {data_col+1}, 跳过数据 (仰角={elevation_val}, 吊重={lifting_cap_val}).")
                     continue


                results.append({
                    'TruckCraneID': truck_crane_id,
                    'ConditionID': None, # 副臂工况没有ConditionID，填充None
                    'SpeWorkCondition': None, # 副臂工况没有主臂工况名称，填充None
                    'TruckCraneRange': None, # 副臂工况没有主臂幅度，填充None
                    'TruckCraneMainArmLen': None, # 副臂工况没有主臂长度的概念直接体现在这里，填充None
                    'TruckCraneRatedLiftingCap': None, # 副臂工况没有主臂额定吊重，填充None
                    'IsJibHosCon': "是",
                    'SecondSpeWorkCondition': final_second_spe_work_condition_1,
                    'SecondElevation': elevation_val,
                    'SecondMainArmLen': range_val, # 副臂工作幅度，从第二行提取
                    'SecondTruckCraneRatedLiftingCap': lifting_cap_val
                })
        
        # --- 处理第二个副臂工况 ---
        # 尝试从第一行第五列（索引4）获取第二个工况名称 (假设间隔3列)
        # 从文件内容第一行获取具体工况名称，如果为空则使用文件名中的副臂工况名称作为 fallback
        jib_content_condition_2 = df.iloc[0, 4] if df.shape[1] > 4 and pd.notna(df.iloc[0, 4]) else ""
        if not isinstance(jib_content_condition_2, str): # Ensure it's a string
            jib_content_condition_2 = str(jib_content_condition_2)
        jib_content_condition_2 = jib_content_condition_2.strip()
        
        # 构建最终的 SecondSpeWorkCondition
        final_second_spe_work_condition_2 = jib_condition_from_filename
        if jib_content_condition_2:
            final_second_spe_work_condition_2 = f"{final_second_spe_work_condition_2}, {jib_content_condition_2}"
        elif not final_second_spe_work_condition_2: # If both are empty, use a default
            final_second_spe_work_condition_2 = "未知副臂工况"

        print(f"  - 识别到第二个副臂工况名称 (文件内容): '{jib_content_condition_2}', 最终输出: '{final_second_spe_work_condition_2}'")

        # 第二个工况的仰角在第八列 (索引 7), 从第3行 (索引 2) 开始
        elevations_2 = df.iloc[2:, 7].values
        # 第二个工况的幅度在第二行 (索引 1), 列索引 4, 5, 6
        ranges_2_cols = [4, 5, 6]
        # 第二个工况的数据列是 5, 6, 7 (索引 4, 5, 6)
        data_cols_2 = [4, 5, 6]

        # 提取幅度值
        ranges_2_values = [df.iloc[1, col] for col in ranges_2_cols if df.shape[1] > col and pd.notna(df.iloc[1, col])]
        print(f"  - 第二个工况幅度值: {ranges_2_values}")

        # 循环处理第二个工况的数据
        for i, elevation in enumerate(elevations_2):
            if pd.isna(elevation) or (isinstance(elevation, str) and not elevation.strip()): continue
            try:
                 elevation_val = float(str(elevation).strip())
            except ValueError:
                 print(f"Warning: 无法解析第二个工况仰角值 '{elevation}' 在行 {i+3}, 跳过.")
                 continue

            # 遍历对应的数据列提取吊重
            for j, data_col in enumerate(data_cols_2):
                if df.shape[1] <= data_col: continue # 避免列越界
                lifting_cap = df.iloc[i+2, data_col]

                if pd.isna(lifting_cap) or (isinstance(lifting_cap, str) and not str(lifting_cap).strip()):
                     continue # 跳过空值或只有空白字符串的单元格
                
                try:
                    lifting_cap_val = float(str(lifting_cap).strip())
                except ValueError:
                     print(f"Warning: 无法解析第二个工况额定吊重值 '{lifting_cap}' 在行 {i+3}, 列 {data_col+1}, 跳过.")
                     continue

                if lifting_cap_val <= 0: continue # 跳过小于等于0的吊重

                # 查找当前列对应的幅度值
                current_range = None
                if j < len(ranges_2_values): # 使用索引 j 来对应幅度值列表
                     current_range = ranges_2_values[j]

                if current_range is None or (isinstance(current_range, str) and not str(current_range).strip()):
                     print(f"Warning: 第二个工况在列 {data_col+1} 未找到对应幅度值，跳过数据 (仰角={elevation_val}, 吊重={lifting_cap_val}).")
                     continue
                
                try:
                     range_val = float(str(current_range).strip())
                except ValueError:
                     print(f"Warning: 无法解析第二个工况幅度值 '{current_range}' 在列 {data_col+1}, 跳过数据 (仰角={elevation_val}, 吊重={lifting_cap_val}).")
                     continue

                results.append({
                    'TruckCraneID': truck_crane_id,
                    'ConditionID': None,
                    'SpeWorkCondition': None,
                    'TruckCraneRange': None, # 副臂工况没有主臂幅度
                    'TruckCraneMainArmLen': None,
                    'TruckCraneRatedLiftingCap': None,
                    'IsJibHosCon': "是",
                    'SecondSpeWorkCondition': final_second_spe_work_condition_2,
                    'SecondElevation': elevation_val,
                    'SecondMainArmLen': range_val, # 副臂工作幅度，从第二行提取
                    'SecondTruckCraneRatedLiftingCap': lifting_cap_val
                })

        result_df = pd.DataFrame(results, columns=ALL_REQUIRED_COLUMNS)
        
        if result_df.empty:
            raise ValueError("未能从副臂文件提取到有效数据")

        # 确保副臂相关的数值列是数值类型
        for col in ['SecondElevation', 'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap']:
             if col in result_df.columns:
                  result_df[col] = pd.to_numeric(result_df[col], errors='coerce')

        # 确保主臂相关的数值列填充默认值
        for col in ['ConditionID', 'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap']:
             if col in result_df.columns:
                 result_df[col] = pd.to_numeric(result_df[col], errors='coerce').fillna(np.nan)

        # 确保字符串列填充默认值""或"是"
        for col in ['SpeWorkCondition', 'IsJibHosCon', 'SecondSpeWorkCondition']:
             if col in result_df.columns:
                 result_df[col] = result_df[col].astype(str).replace('nan', '').replace('None', '').fillna('')
        result_df['IsJibHosCon'] = "是"

        return result_df

    except Exception as e:
        # 打印更详细的错误信息，包括文件名和错误内容
        print(f"Error processing jib file {os.path.basename(file_path)}: {e}")
        # 捕获并重新抛出更明确的错误
        raise ValueError(f"处理主臂+副臂文件 '{os.path.basename(file_path)}' 时出错: {str(e)}")

def process_multiple_files(file_paths):
    """
    处理多个Excel文件，将数据融合并合并结果到496行。
    Args:
        file_paths (list): Excel文件路径列表
    Returns:
        tuple: (合并的DataFrame, 汽车吊型号列表, 主臂文件统计列表, 副臂文件统计列表)
    """
    if not file_paths:
        raise ValueError("没有选择文件")

    main_data_list = []  # 存储主臂工况df列表
    jib_data_list = []   # 存储副臂工况df列表
    truck_crane_ids = set()
    processed_count = 0
    error_count = 0

    main_file_stats = [] # 存储每个主臂文件的统计信息 (文件名, 条数)
    jib_file_stats = []  # 存储每个副臂文件的统计信息 (文件名, 条数)
    
    # 分类并初步处理文件
    for file_path in file_paths:
        try:
            print(f"\n处理文件: {os.path.basename(file_path)}")
            file_name = os.path.basename(file_path)
            _, _, _, is_jib, _ = extract_info_from_filename(file_name)

            if is_jib:
                df = process_jib_excel_file(file_path)
                jib_data_list.append(df)
                jib_file_stats.append((file_name, len(df))) # 记录文件名和条数
            else:
                df = process_main_excel_file(file_path)
                main_data_list.append(df)
                main_file_stats.append((file_name, len(df))) # 记录文件名和条数
                
            # 提取汽车吊型号（从任一成功处理的文件中获取）
            if not df.empty and 'TruckCraneID' in df.columns:
                 crane_id = df['TruckCraneID'].iloc[0] # 假设同一批文件是同一型号
                 if pd.notna(crane_id) and crane_id.strip():
                      truck_crane_ids.add(crane_id)

            processed_count += 1
            print(f"  - 成功处理: {len(df)} 行原始数据")
        except ValueError as ve:
            error_count += 1
            print(f"  - 错误: 处理文件 '{os.path.basename(file_path)}' 时出错: {str(ve)}") # 打印具体错误信息
        except Exception as e:
             error_count += 1
             print(f"  - 未预期的错误: 处理文件 '{os.path.basename(file_path)}' 时出错: {str(e)}") # 打印具体错误信息

    print(f"\n处理统计:")
    print(f"  - 成功处理: {processed_count} 个文件")
    print(f"  - 处理失败: {error_count} 个文件")

    if not main_data_list and not jib_data_list:
        raise ValueError("所有文件处理失败，未能提取任何有效数据")

    # 合并所有主臂数据
    if main_data_list:
        df_main = pd.concat(main_data_list, ignore_index=True)
    else:
         # 如果没有主臂工况数据，创建一个空的DF，包含所有必需列，IsJibHosCon默认为"否"
         df_main = pd.DataFrame(columns=ALL_REQUIRED_COLUMNS)
         df_main['IsJibHosCon'] = "否"

    # 合并所有副臂数据
    if jib_data_list:
        df_jib = pd.concat(jib_data_list, ignore_index=True)
    else:
        # 如果没有副臂工况数据，创建一个空的DF，包含所有必需列，IsJibHosCon默认为"是"
        df_jib = pd.DataFrame(columns=ALL_REQUIRED_COLUMNS)
        df_jib['IsJibHosCon'] = "是"
    
    # --- 实现数据融合和合并逻辑 (生成496行) ---
    final_merged_df = pd.DataFrame(columns=ALL_REQUIRED_COLUMNS) # 最终的DF，共496行

    # 确保主臂数据条数 >= 276，以便进行融合
    if len(df_main) < len(df_jib):
         print(f"Warning: 主臂数据 ({len(df_main)} 行) 少于副臂数据 ({len(df_jib)} 行). 无法进行融合操作以得到496行.")
         # 这种情况下，无法按照要求的496行格式输出。可以考虑直接输出总的772行或者报错。
         # 根据需求，这里选择报错或者返回空DF
         # 为了不中断流程，这里先返回一个包含所有主臂数据和副臂数据的DF，并打印警告。
         # 更好的做法是根据用户需求决定是报错还是切换到其他输出模式
         print("将直接合并所有主臂和副臂数据 (总计 772 行).")
         final_merged_df = pd.concat([df_main, df_jib], ignore_index=True)
         # 返回合并后的772行数据，并保留原始统计信息
         return final_merged_df, list(truck_crane_ids), main_file_stats, jib_file_stats

    # 对主臂数据进行排序，确定前276行和后220行
    # 排序规则：汽车吊型号 -> 工况编号 -> 工况名称 -> 主臂长 -> 幅度 -> 额定吊重
    sort_keys_main = ['TruckCraneID', 'ConditionID', 'SpeWorkCondition', 'TruckCraneMainArmLen', 'TruckCraneRange']
    # 处理NaN值进行排序
    temp_df_main_sort = df_main.copy()
    for col in sort_keys_main:
        if col in temp_df_main_sort.columns:
            temp_df_main_sort[col] = pd.to_numeric(temp_df_main_sort[col], errors='coerce').fillna(np.inf) # 数值列NaN填充无穷大
    df_main_sorted = df_main.iloc[temp_df_main_sort.sort_values(by=sort_keys_main).index].reset_index(drop=True)

    # 分割主臂数据
    df_main_part1 = df_main_sorted.head(len(df_jib)) # 前276行 (与副臂数据行数一致)
    df_main_part2 = df_main_sorted.iloc[len(df_jib):] # 后220行

    # 准备副臂数据 (只保留需要融合的右侧列 + IsJibHosCon)
    # df_jib 已经包含了所有列且IsJibHosCon="是"，主臂列为默认值
    df_jib_for_merge = df_jib.copy()

    # --- 融合数据 (前276行) ---
    # 创建一个空的DF用于存储融合后的前276行
    fused_part1 = pd.DataFrame(index=range(len(df_jib)), columns=ALL_REQUIRED_COLUMNS)

    # 填充左侧主臂数据 (来自df_main_part1)
    for col in ['TruckCraneID', 'ConditionID', 'SpeWorkCondition', 'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap']:
         if col in df_main_part1.columns:
              fused_part1[col] = df_main_part1[col].reset_index(drop=True)

    # 填充右侧副臂数据 (来自df_jib)
    for col in ['SecondSpeWorkCondition', 'SecondElevation', 'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap']:
         if col in df_jib_for_merge.columns:
              fused_part1[col] = df_jib_for_merge[col].reset_index(drop=True)

    # 设置融合部分的 IsJibHosCon 为 "是"
    fused_part1['IsJibHosCon'] = "是"

    # 确保融合部分的数据类型正确 (特别是数值列)
    for col in ['ConditionID', 'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap', 'SecondElevation', 'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap']:
         if col in fused_part1.columns:
              fused_part1[col] = pd.to_numeric(fused_part1[col], errors='coerce')
    
    # 确保字符串列填充默认值
    for col in ['SpeWorkCondition', 'IsJibHosCon', 'SecondSpeWorkCondition', 'TruckCraneID']:
         if col in fused_part1.columns:
              fused_part1[col] = fused_part1[col].astype(str).replace('nan', '').replace('None', '').fillna('')
    fused_part1['IsJibHosCon'] = "是" # 再次强制设置为是

    # --- 合并两部分数据 ---
    # 后220行 (纯主臂数据)，确保Second列为默认值，IsJibHosCon为否
    df_main_part2_final = df_main_part2.copy()
    df_main_part2_final['IsJibHosCon'] = "否"
    for col in ['SecondSpeWorkCondition', 'SecondElevation', 'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap']:
         if col in df_main_part2_final.columns:
             if df_main_part2_final[col].dtype == 'object':
                 df_main_part2_final[col] = "" # 字符串列默认值
             else:
                 df_main_part2_final[col] = 0.0 # 数值列默认值

    # 纵向合并融合部分和剩余主臂部分
    final_merged_df = pd.concat([fused_part1, df_main_part2_final], ignore_index=True)

    # 最终按照您要求的顺序排序
    # 排序规则：汽车吊型号 -> 工况编号 -> 工况名称 -> 主臂长 -> 幅度 -> 额定吊重
    user_sort_keys = ['ConditionID', 'SpeWorkCondition', 'TruckCraneMainArmLen', 'TruckCraneRange', 'TruckCraneRatedLiftingCap']

    # 处理排序键中的NaN和非数字
    temp_df_final_sort = final_merged_df.copy()
    for col in user_sort_keys:
        if col in temp_df_final_sort.columns:
            temp_df_final_sort[col] = pd.to_numeric(temp_df_final_sort[col], errors='coerce').fillna(np.inf)

    # IsJibHosCon排序 (否=0, 是=1)
    temp_df_final_sort['IsJibHosCon_sort'] = temp_df_final_sort['IsJibHosCon'].apply(lambda x: 0 if x == "否" else 1)
    
    # Combine TruckCraneID, IsJibHosCon_sort, and user_sort_keys for final sorting
    final_combined_sort_keys = ['TruckCraneID', 'IsJibHosCon_sort'] + user_sort_keys
    
    final_merged_df = final_merged_df.iloc[temp_df_final_sort.sort_values(by=final_combined_sort_keys).index].reset_index(drop=True)
    
    # 删除辅助排序列
    if 'IsJibHosCon_sort' in final_merged_df.columns:
         final_merged_df = final_merged_df.drop(columns=['IsJibHosCon_sort'])

    # 确保最终DF的列顺序正确
    final_merged_df = final_merged_df[ALL_REQUIRED_COLUMNS]

    # 确保最终输出的Total行数是496
    if len(final_merged_df) != 496:
         print(f"Warning: 最终合并的数据行数不等于496，实际为 {len(final_merged_df)} 行.")
         # 可以考虑在这里进行截断或填充到496行，但这可能会丢失/增加数据，与原始意图冲突。
         # 目前的逻辑是如果副臂数据不是276行，或者主臂数据不是496行，最终行数会不等于496。
         # 为了符合要求，这里假设原始数据量是固定的，否则需要更复杂的处理或提示用户。

    return final_merged_df, list(truck_crane_ids), main_file_stats, jib_file_stats

def main():
    """主函数：提供文件选择界面并处理选择的文件"""
    root = tk.Tk()
    root.title("汽车吊数据转换工具")
    root.withdraw()  # 隐藏主窗口

    print("原始Excel转数据库格式工具")
    print("============================\n")
    print("本工具可以一次性处理主臂吊装工况和主臂+副臂吊装工况的Excel文件")
    print("文件名格式要求:")
    print("  - 主臂工况格式: 工况编号-(汽车吊型号)-(工况名称).xlsx")
    print("  - 副臂工况格式: (汽车吊型号)-(主臂+副臂工况名称).xlsx")
    print("============================\n")
    print("请选择要处理的Excel文件(可同时选择主臂工况和主臂+副臂工况文件)...\n")

    file_paths = filedialog.askopenfilenames(
        title="选择需要处理的Excel文件 (主臂工况和主臂+副臂工况)",
        filetypes=[("Excel文件", "*.xlsx *.xls")]
    )

    if not file_paths:
        print("未选择任何文件，程序退出")
        return

    # 分类统计文件名（用于弹窗显示和后续统计）
    main_files = [] # 文件名列表
    jib_files = []  # 文件名列表
    error_files = [] # 文件名列表
    for file_path in file_paths:
        try:
            file_name = os.path.basename(file_path)
            # 使用 extract_info_from_filename 来判断文件类型
            _, _, _, is_jib, _ = extract_info_from_filename(file_name)
            if is_jib:
                jib_files.append(file_name)
            else:
                main_files.append(file_name)
        except Exception as e:
            error_files.append(f"{os.path.basename(file_path)} (无法识别: {e})") # 记录无法识别的文件

    # 弹窗提醒文件分类
    msg_parts = []
    msg_parts.append("文件分类如下：\n")
    
    msg_parts.append(f"主臂工况Excel表格 ({len(main_files)} 个):")
    if main_files:
        msg_parts.extend(main_files)
    else:
        msg_parts.append("无")
    msg_parts.append("\n") # 添加空行

    msg_parts.append(f"主臂+副臂工况Excel表格 ({len(jib_files)} 个):")
    if jib_files:
        msg_parts.extend(jib_files)
    else:
        msg_parts.append("无")
    msg_parts.append("\n") # 添加空行
    
    if error_files:
        msg_parts.append(f"无法识别的文件 ({len(error_files)} 个):")
        msg_parts.extend(error_files)
        msg_parts.append("\n") # 添加空行

    messagebox.showinfo("文件类型分类", "\n".join(msg_parts))


    try:
        print(f"选择了 {len(file_paths)} 个文件")
        # 调用process_multiple_files并获取文件统计信息
        merged_df, truck_crane_ids, main_file_stats, jib_file_stats = process_multiple_files(file_paths)

        # 生成输出文件名和路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if truck_crane_ids and len(truck_crane_ids) == 1:
            base_name = f"{list(truck_crane_ids)[0]}-额定起重量表-{timestamp}.xlsx"
        else:
            base_name = f"合并额定起重量表-{timestamp}.xlsx" # 更通用，避免文件名过长或无效字符

        # 默认输出到第一个输入文件的目录，如果无文件选择，则不会到这里
        # 如果file_paths为空，则不会进入try块，所以os.path.dirname(file_paths[0])是安全的
        output_dir = os.path.dirname(file_paths[0])
        output_path = os.path.join(output_dir, base_name)

        # 保存转换后的数据
        if not merged_df.empty:
            merged_df.to_excel(output_path, index=False)
            print(f"\n转换后的Excel文件已保存到: {output_path}")
        else:
            print("\n没有生成有效数据，不创建Excel文件。")
            output_path = "" # 清空路径，避免后续错误

        # 统计信息输出到txt
        stat_lines = []
        stat_lines.append("========== 文件处理详情 ==========")
        stat_lines.append("")
        stat_lines.append(f"总共选择了 {len(file_paths)} 个文件")
        stat_lines.append(f"成功处理的文件个数: {len(main_file_stats) + len(jib_file_stats)}")
        stat_lines.append(f"无法识别或处理失败的文件个数: {len(error_files)}")
        stat_lines.append("")

        # 按文件列出主臂工况统计
        stat_lines.append(f"主臂工况Excel表格个数: {len(main_file_stats)}")
        stat_lines.append("主臂工况Excel文件名及数据条数:")
        if main_file_stats:
            for file_name, row_count in main_file_stats:
                stat_lines.append(f"  {file_name}: {row_count} 条额定吊重数据")
        else:
            stat_lines.append("  无")
        stat_lines.append("")

        # 按文件列出主臂+副臂工况统计
        stat_lines.append(f"主臂+副臂工况Excel表格个数: {len(jib_file_stats)}")
        stat_lines.append("主臂+副臂工况Excel文件名及数据条数:")
        if jib_file_stats:
            for file_name, row_count in jib_file_stats:
                 stat_lines.append(f"  {file_name}: {row_count} 条额定吊重数据")
        else:
             stat_lines.append("  无")
        stat_lines.append("")

        # 现有的总统计信息 (基于最终合并后的数据)
        stat_lines.append("========== 汇总统计 ==========")
        stat_lines.append("")
        total_rows = len(merged_df) if not merged_df.empty else 0 # 使用最终合并后的DF总行数
        rows_with_jib = merged_df[merged_df['IsJibHosCon'] == "是"].shape[0] if not merged_df.empty and 'IsJibHosCon' in merged_df.columns else 0
        unique_crane_models = merged_df['TruckCraneID'].nunique() if not merged_df.empty and 'TruckCraneID' in merged_df.columns else 0

        stat_lines.append(f"总计数据行数 (合并后): {total_rows} 行")
        stat_lines.append(f"包含副臂数据的行数: {rows_with_jib} 行")
        stat_lines.append(f"纯主臂数据行数: {total_rows - rows_with_jib} 行") # 注意：在融合模式下，纯主臂数据行数是剩余的220行
        stat_lines.append(f"汽车吊型号数量: {unique_crane_models} 个")

        # 主臂工况名称和数据条数 (基于最终合并后的数据中IsJibHosCon为否的行)
        if not merged_df.empty and 'SpeWorkCondition' in merged_df.columns:
             # 过滤出IsJibHosCon为否的行，并SpeWorkCondition非空
             main_df_final = merged_df[(merged_df['IsJibHosCon'] == "否") & (merged_df['SpeWorkCondition'].astype(str).str.strip() != "")].copy() # 创建副本并过滤
             main_names_final = main_df_final['SpeWorkCondition'].astype(str).str.strip().unique().tolist() # 获取唯一名称列表
             
             stat_lines.append(f"\n主臂工况名称个数 (最终表格): {len(main_names_final)}")
             stat_lines.append("主臂工况名称及对应数据条数:")
             if main_names_final:
                 for name in main_names_final:
                     count = main_df_final[main_df_final['SpeWorkCondition'].astype(str).str.strip() == name].shape[0]
                     stat_lines.append(f"  '{name}': {count} 条") # 加引号避免空格问题
             else:
                  stat_lines.append("  无有效纯主臂工况数据")
        else:
             stat_lines.append("\n主臂工况名称个数 (最终表格): 0")
             stat_lines.append("主臂工况名称及对应数据条数:\n  无有效纯主臂工况数据")


        # 副臂工况名称和数据条数 (基于最终合并后的数据中IsJibHosCon为是的行)
        if not merged_df.empty and 'SecondSpeWorkCondition' in merged_df.columns:
            # 过滤出IsJibHosCon为是的行，并SecondSpeWorkCondition非空
            jib_df_final = merged_df[(merged_df['IsJibHosCon'] == "是") & (merged_df['SecondSpeWorkCondition'].astype(str).str.strip() != "")].copy() # 创建副本并过滤
            # 过滤掉空的副臂工况名称
            jib_names_final = jib_df_final['SecondSpeWorkCondition'].astype(str).str.strip().unique().tolist() # 获取唯一名称列表

            stat_lines.append(f"\n主臂+副臂工况名称个数 (最终表格): {len(jib_names_final)}")
            stat_lines.append("主臂+副臂工况名称及对应数据条数:")
            if jib_names_final:
                for name in jib_names_final:
                    count = jib_df_final[jib_df_final['SecondSpeWorkCondition'].astype(str).str.strip() == name].shape[0]
                    stat_lines.append(f"  '{name}': {count} 条") # 加引号
            else:
                 stat_lines.append("  无有效主臂+副臂工况数据")
        else:
             stat_lines.append("\n主臂+副臂工况名称个数 (最终表格): 0")
             stat_lines.append("主臂+副臂工况名称及对应数据条数:\n  无有效主臂+副臂工况数据")


        stat_lines.append("\n--- 结束 ---") # 添加结束标记
        stat_txt = "\n".join(stat_lines)

        stat_filename = f"统计信息-{timestamp}.txt"
        # 确定统计文件保存目录，如果没有生成excel，则默认保存在第一个输入文件目录
        stat_output_dir = output_dir if output_path else (os.path.dirname(file_paths[0]) if file_paths else ".") # 如果file_paths也为空，则保存在当前目录
        stat_path = os.path.join(stat_output_dir, stat_filename)

        try:
            with open(stat_path, 'w', encoding='utf-8') as f:
                f.write(stat_txt)
            print(f"\n统计信息已保存到: {stat_path}")
        except Exception as write_error:
             print(f"\n错误: 无法写入统计信息文件 {stat_path}: {write_error}")


        # 显示成功消息
        success_msg = (
            f"成功处理 {len(file_paths)} 个文件\n"
            f"总计数据: {total_rows} 行\n"
            f"包含副臂数据的行数: {rows_with_jib} 行\n"
            f"纯主臂数据行数: {total_rows - rows_with_jib} 行\n"
            f"汽车吊型号数量: {unique_crane_models} 个\n"
            f"不同主臂工况数量: {merged_df['TruckCraneID'].nunique()} 个\n"
            f"输出Excel文件: {os.path.basename(output_path)}\n"
            f"输出统计Txt文件: {os.path.basename(stat_path)}"
        )
                      
        messagebox.showinfo("处理完成", success_msg)

        # 询问用户是否打开生成的文件和所在的文件夹
        if messagebox.askyesno("操作完成", 
                              f"文件处理完成！\n\n" +
                              f"统计信息已保存到:\n{stat_path}\n\n" +
                              f"转换后的Excel已保存到:\n{output_path}\n\n" +
                              f"是否现在打开文件和所在的文件夹？"):
             import subprocess
             import platform

             # 尝试打开统计文件
             if os.path.exists(stat_path):
                  try:
                      if platform.system() == "Windows":
                          os.startfile(stat_path)
                      elif platform.system() == "Darwin":
                          subprocess.Popen(["open", stat_path])
                      else:
                          subprocess.Popen(["xdg-open", stat_path])
                  except FileNotFoundError:
                       messagebox.showerror("错误", f"无法找到打开统计文件 {stat_path} 的应用程序。")
                  except Exception as open_error:
                       messagebox.showerror("打开统计文件错误", f"打开统计文件时发生错误: {open_error}")

             # 尝试打开Excel文件
             if output_path and os.path.exists(output_path):
                  try:
                      if platform.system() == "Windows":
                          os.startfile(output_path)
                      elif platform.system() == "Darwin":
                          subprocess.Popen(["open", output_path])
                      else:
                          subprocess.Popen(["xdg-open", output_path])
                  except FileNotFoundError:
                       messagebox.showerror("错误", f"无法找到打开Excel文件 {output_path} 的应用程序。")
                  except Exception as open_error:
                       messagebox.showerror("打开Excel文件错误", f"打开Excel文件时发生错误: {open_error}")

             # 尝试打开输出文件夹
             if output_dir and os.path.exists(output_dir):
                  try:
                       if platform.system() == "Windows":
                           os.startfile(output_dir)
                       elif platform.system() == "Darwin":
                           subprocess.Popen(["open", output_dir])
                       else:
                           subprocess.Popen(["xdg-open", output_dir])
                  except FileNotFoundError:
                       messagebox.showerror("错误", f"无法找到打开文件夹 {output_dir} 的应用程序。")
                  except Exception as open_error:
                       messagebox.showerror("打开文件夹错误", f"打开文件夹时发生错误: {open_error}")


    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(f"\n错误: {error_msg}")
        messagebox.showerror("处理错误", error_msg)

    # 让用户决定是否继续
    if messagebox.askyesno("操作完成", "是否关闭程序?"):
        root.destroy()
    else:
        # 如果重新启动，需要清空文件选择，避免重复处理
        # 这里简单地退出当前Tkinter实例并重新调用main
        # 注意：这可能会导致多次Tkinter实例。
        # 更优方案是修改main函数逻辑，使其能重复使用同一Tkinter实例或进行更彻底的清理。
        # 当前实现能工作，但在某些环境下可能行为异常。
        root.destroy()
        # 重置全局状态或退出进程，这里选择退出
        import sys
        sys.exit()


if __name__ == "__main__":
    main()

