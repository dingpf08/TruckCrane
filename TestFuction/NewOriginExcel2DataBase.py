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
    - 主臂+副臂工况：IsJibHosCon为"是"，副臂相关字段填充对应数据。
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
               对于副臂工况，工况编号为None
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
        truck_crane_id, _, _, is_jib, jib_condition_from_filename = extract_info_from_filename(file_name)
        
        results = []
        
        # --- 处理第一个副臂工况 ---
        # 尝试从第一行第二列（索引1）获取第一个工况名称
        jib_condition_1 = df.iloc[0, 1] if df.shape[1] > 1 and pd.notna(df.iloc[0, 1]) else f"{jib_condition_from_filename}_工况1"
        print(f"  - 识别到第一个副臂工况名称: {jib_condition_1}")
        
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
                    'ConditionID': None, # 副臂工况没有ConditionID
                    'SpeWorkCondition': None, # 副臂工况没有主臂工况名称
                    'TruckCraneRange': range_val, # 副臂工况的Range
                    'TruckCraneMainArmLen': None, # 副臂工况没有主臂长度的概念在数据中直接体现
                    'TruckCraneRatedLiftingCap': None, # 副臂工况的主臂额定吊重不适用
                    'IsJibHosCon': "是",
                    'SecondSpeWorkCondition': jib_condition_1,
                    'SecondElevation': elevation_val,
                    'SecondMainArmLen': None, # 副臂主臂长可能需要从名称或仰角推断，这里先留空
                    'SecondTruckCraneRatedLiftingCap': lifting_cap_val
                })
        
        # --- 处理第二个副臂工况 ---
        # 尝试从第一行第五列（索引4）获取第二个工况名称 (假设间隔3列)
        jib_condition_2 = df.iloc[0, 4] if df.shape[1] > 4 and pd.notna(df.iloc[0, 4]) else f"{jib_condition_from_filename}_工况2"
        print(f"  - 识别到第二个副臂工况名称: {jib_condition_2}")

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
                    'TruckCraneRange': range_val, # 副臂工况的Range
                    'TruckCraneMainArmLen': None,
                    'TruckCraneRatedLiftingCap': None,
                    'IsJibHosCon': "是",
                    'SecondSpeWorkCondition': jib_condition_2,
                    'SecondElevation': elevation_val,
                    'SecondMainArmLen': None, # 副臂主臂长
                    'SecondTruckCraneRatedLiftingCap': lifting_cap_val
                })

        result_df = pd.DataFrame(results)
        
        if result_df.empty:
            raise ValueError("未能从副臂文件提取到有效数据")

        # 副臂数据不需要主臂工况的排序字段，但需要确保所有列存在
        # 在 process_multiple_files 中会进行最终合并和列处理
        
        return result_df

    except Exception as e:
        # 打印更详细的错误信息，包括文件名和错误内容
        print(f"Error processing jib file {os.path.basename(file_path)}: {e}")
        # 捕获并重新抛出更明确的错误
        raise ValueError(f"处理主臂+副臂文件 '{os.path.basename(file_path)}' 时出错: {str(e)}")

def process_excel_file(file_path):
    """
    处理单个Excel文件，将交叉表转换为数据库格式
    主臂工况：行=幅度，列=主臂长，数据区=额定吊重
    Args:
        file_path (str): Excel文件路径
    Returns:
        tuple: (DataFrame, 汽车吊型号, 是否为副臂工况文件)
    """
    # 从文件名提取信息
    file_name = os.path.basename(file_path)
    truck_crane_id, condition_id, work_condition, is_jib, jib_condition = extract_info_from_filename(file_name)
    
    # 根据文件名判断是否为副臂工况文件
    if is_jib:
        # 如果是副臂工况文件，使用专门的处理函数
        # process_jib_excel_file 返回的是 DataFrame，直接返回即可
        print(f"Detected jib file: {file_name}") # 添加日志确认识别到副臂文件
        return process_jib_excel_file(file_path), truck_crane_id, True
    
    # 以下是处理主臂工况文件的代码
    try:
        print(f"  - 开始读取主臂文件: {file_path}") # 修改日志以区分
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        if df.empty:
            raise ValueError("Excel文件不包含数据")
        print(f"  - 主臂表格尺寸: {df.shape[0]}行 x {df.shape[1]}列") # 修改日志以区分
        if df.shape[0] < 2 or df.shape[1] < 2:
            raise ValueError("Excel表格至少需要2行2列")
        # 获取幅度（行索引，从第2行开始，第1列）
        ranges = df.iloc[1:, 0].values
        # 获取主臂长（列索引，第1行，从第2列开始）
        arm_lengths = df.iloc[0, 1:].values
        # 数据清理
        clean_ranges = []
        for i, val in enumerate(ranges):
            try:
                if pd.isna(val):
                    continue
                if isinstance(val, str):
                    clean_val = ''.join(c for c in val if c.isdigit() or c == '.')
                    if clean_val:
                        clean_ranges.append((i, float(clean_val)))
                else:
                    clean_ranges.append((i, float(val)))
            except Exception as e:
                print(f"Warning: 无法解析幅度值 '{val}' 在行 {i+2}: {str(e)}")
        if not clean_ranges:
            raise ValueError("未能提取到有效的幅度数据")
        clean_arm_lengths = []
        for j, val in enumerate(arm_lengths):
            try:
                if pd.isna(val):
                    continue
                if isinstance(val, str):
                    clean_val = ''.join(c for c in val if c.isdigit() or c == '.')
                    if clean_val:
                        clean_arm_lengths.append((j, float(clean_val)))
                else:
                    clean_arm_lengths.append((j, float(val)))
            except Exception as e:
                print(f"Warning: 无法解析主臂长值 '{val}' 在列 {j+2}: {str(e)}")
        if not clean_arm_lengths:
            raise ValueError("未能提取到有效的主臂长数据")
        results = []
        for i, range_val in clean_ranges:
            for j, arm_len in clean_arm_lengths:
                try:
                    lifting_cap = df.iloc[i+1, j+1]
                    if pd.isna(lifting_cap):
                        continue
                    if isinstance(lifting_cap, str):
                        lifting_cap = lifting_cap.strip()
                        if not lifting_cap:
                            continue
                        clean_val = ''.join(c for c in lifting_cap if c.isdigit() or c == '.')
                        if not clean_val:
                            continue
                        try:
                            lifting_cap = float(clean_val)
                        except:
                            print(f"Warning: 无法将值 '{lifting_cap}' 转换为数字，跳过 (行={i+2}, 列={j+2})")
                            continue
                    else:
                        try:
                            lifting_cap = float(lifting_cap)
                        except:
                            print(f"Warning: 无法将值 '{lifting_cap}' 转换为数字，跳过 (行={i+2}, 列={j+2})")
                            continue
                    if lifting_cap <= 0:
                        continue
                    results.append({
                        'TruckCraneID': truck_crane_id,
                        'ConditionID': condition_id,
                        'SpeWorkCondition': work_condition,
                        'TruckCraneRange': range_val,
                        'TruckCraneMainArmLen': arm_len,
                        'TruckCraneRatedLiftingCap': lifting_cap,
                        'IsJibHosCon': "否",
                        'SecondSpeWorkCondition': "",
                        'SecondElevation': 0,
                        'SecondMainArmLen': 0,
                        'SecondTruckCraneRatedLiftingCap': 0
                    })
                except Exception as e:
                    print(f"Warning: 处理数据时出错 (行={i+2}, 列={j+2}): {str(e)}")
        result_df = pd.DataFrame(results)
        if result_df.empty:
            raise ValueError("无法从Excel提取有效数据")
        return result_df, truck_crane_id, False # 主臂工况返回False
    except Exception as e:
        raise ValueError(f"处理文件 '{file_path}' 时出错: {str(e)}")

def process_multiple_files(file_paths):
    """
    处理多个Excel文件并合并结果
    Args:
        file_paths (list): Excel文件路径列表
    Returns:
        tuple: (合并的DataFrame, 汽车吊型号列表, 主臂文件统计列表, 副臂文件统计列表)
    """
    if not file_paths:
        raise ValueError("没有选择文件")
    main_data = []  # 存储主臂工况df
    jib_data = []   # 存储副臂工况df
    truck_crane_ids = set()
    processed_count = 0
    error_count = 0

    # 新增：存储每个文件的统计信息 (文件名, 条数)
    main_file_stats = []
    jib_file_stats = []

    for file_path in file_paths:
        try:
            print(f"\n处理文件: {os.path.basename(file_path)}")
            df, truck_crane_id, is_jib = process_excel_file(file_path)
            file_name = os.path.basename(file_path) # 获取文件名

            # 根据文件类型分别存储数据和统计信息
            if is_jib:
                jib_data.append(df)
                jib_file_stats.append((file_name, len(df))) # 记录文件名和条数
            else:
                main_data.append(df)
                main_file_stats.append((file_name, len(df))) # 记录文件名和条数

            truck_crane_ids.add(truck_crane_id)
            processed_count += 1
            print(f"  - 成功处理: {len(df)} 行数据")
        except Exception as e:
            error_count += 1
            print(f"  - 错误: 处理文件 '{os.path.basename(file_path)}' 时出错: {str(e)}") # 明确哪个文件出错

    print(f"\n处理统计:")
    print(f"  - 成功处理: {processed_count} 个文件")
    print(f"  - 处理失败: {error_count} 个文件")

    if not main_data and not jib_data:
        raise ValueError("所有文件处理失败，未能提取任何有效数据")

    # 合并主臂数据
    if main_data:
        merged_main_df = pd.concat(main_data, ignore_index=True)
    else:
         # 如果没有主臂工况数据，创建一个空的DF，包含所有必需列
         merged_main_df = pd.DataFrame(columns=[\
              'TruckCraneID', 'ConditionID', 'SpeWorkCondition',
              'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap',\
              'IsJibHosCon', 'SecondSpeWorkCondition', 'SecondElevation',\
              'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap'\
         ])

    # 合并副臂数据
    if jib_data:
        merged_jib_df = pd.concat(jib_data, ignore_index=True)
    else:
        merged_jib_df = pd.DataFrame(columns=[\
              'TruckCraneID', 'SecondSpeWorkCondition', 'SecondElevation',\
              'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap'\
        ]) # 创建空DF确保列存在

    # 确保主臂数据DF包含所有必需列（即使只有副臂文件被选中）
    required_columns = [\
        'TruckCraneID', 'ConditionID', 'SpeWorkCondition',
        'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap',\
        'IsJibHosCon', 'SecondSpeWorkCondition', 'SecondElevation',\
        'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap'\
    ]

    # 添加缺失的列并设置默认值
    for col in required_columns:
        if col not in merged_main_df.columns:
             merged_main_df[col] = 0 if col not in ['TruckCraneID', 'SpeWorkCondition', 'SecondSpeWorkCondition', 'IsJibHosCon'] else ""
        # 确保 IsJibHosCon 默认为 "否"
        if col == 'IsJibHosCon' and merged_main_df[col].dtype != 'object':
             merged_main_df[col] = merged_main_df[col].astype(str).replace('0', '否')


    # 排序：主臂工况编号 -> 主臂长度 -> 主臂额定起重量 (仅对主臂数据进行此排序)
    # 副臂数据将在后续合并，它们的顺序可能需要另外处理或保持解析时的顺序
    # 如果只有副臂数据，这一步不应该执行基于主臂字段的排序
    if not merged_main_df.empty and not main_data: # 如果merged_main_df非空但main_data空，说明是从纯副臂数据构建的空主臂DF
         # 只有副臂数据，不需要按主臂工况字段排序
         pass # 或者可以按副臂相关字段排序
    elif not merged_main_df.empty: # 如果有主臂数据，或者合并了主臂和副臂数据
         # 先确保排序键存在且是非空，避免只有副臂数据时出错
         sort_keys = []
         if 'ConditionID' in merged_main_df.columns and merged_main_df['ConditionID'].dropna().astype(str).str.strip().any(): sort_keys.append('ConditionID')
         if 'TruckCraneMainArmLen' in merged_main_df.columns and merged_main_df['TruckCraneMainArmLen'].dropna().astype(str).str.strip().any(): sort_keys.append('TruckCraneMainArmLen')
         if 'TruckCraneRatedLiftingCap' in merged_main_df.columns and merged_main_df['TruckCraneRatedLiftingCap'].dropna().astype(str).str.strip().any(): sort_keys.append('TruckCraneRatedLiftingCap')

         # 如果有主臂工况相关的排序键，就按这些键排序
         if sort_keys:
             # 过滤出主臂数据部分进行排序，再与其他数据合并？
             # 更简单的做法是对整个DF排序，确保副臂数据不会干扰主臂排序
             # 需要处理None值，将None转换为一个排序友好的值 (如最大或最小值)
             temp_df_for_sort = merged_main_df.copy()
             for key in sort_keys:
                  # 将非数值和None值转换为一个大数，确保它们排在后面
                 temp_df_for_sort[key] = pd.to_numeric(temp_df_for_sort[key], errors='coerce').fillna(np.nan) # 先转数字，非数字变NaN
                 temp_df_for_sort[key] = temp_df_for_sort[key].fillna(temp_df_for_sort[key].max() + 1 if not temp_df_for_sort[key].isnull().all() else 0) # NaN填充一个大数，全NaN填充0

             merged_main_df = merged_main_df.iloc[temp_df_for_sort.sort_values(by=sort_keys).index].reset_index(drop=True)


    # 将副臂数据合并到主臂数据的末尾 (修改合并逻辑，不再是填入)
    # 创建副臂数据的最终格式DF
    if not merged_jib_df.empty:
         print("\n合并副臂工况数据...")
         temp_jib_final_df = pd.DataFrame(index=range(len(merged_jib_df)), columns=required_columns)
         temp_jib_final_df['TruckCraneID'] = merged_jib_df['TruckCraneID']
         temp_jib_final_df['IsJibHosCon'] = "是"
         temp_jib_final_df['SecondSpeWorkCondition'] = merged_jib_df['SecondSpeWorkCondition']
         temp_jib_final_df['SecondElevation'] = merged_jib_df['SecondElevation']
         temp_jib_final_df['SecondMainArmLen'] = merged_jib_df['SecondMainArmLen']
         temp_jib_final_df['SecondTruckCraneRatedLiftingCap'] = merged_jib_df['SecondTruckCraneRatedLiftingCap']

         # 其他列填充默认值
         for col in required_columns:
              if col not in temp_jib_final_df.columns:
                  temp_jib_final_df[col] = 0 if col not in ['TruckCraneID', 'SpeWorkCondition', 'SecondSpeWorkCondition', 'IsJibHosCon'] else ""

         # 将主臂数据和副臂数据合并
         final_merged_df = pd.concat([merged_main_df, temp_jib_final_df], ignore_index=True)
    else:
         final_merged_df = merged_main_df # 如果没有副臂数据，最终DF就是主臂数据

    # 确保最终DF的列顺序正确
    if not final_merged_df.empty:
         final_merged_df = final_merged_df[required_columns]
         # 对整个合并后的DF进行最终排序（例如，按型号和工况类型区分排序）
         # 如果需要区分主臂和副臂的排序，这里需要更复杂的逻辑
         # 暂时保持按主臂字段排序后的结果，副臂数据会追加在后面

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
            base_name = f"多种汽车吊-额定起重量表-{timestamp}.xlsx"
        # 默认输出到第一个输入文件的目录，如果无文件选择，则不会到这里
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
        stat_lines.append("--- 文件处理统计 ---")
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

        # 现有的总统计信息 (基于合并后的数据)
        stat_lines.append("--- 合并数据总统计 ---")
        stat_lines.append("")
        total_rows = len(merged_df) if not merged_df.empty else 0 # 使用最终合并后的DF总行数
        rows_with_jib = merged_df[merged_df['IsJibHosCon'] == "是"].shape[0] if not merged_df.empty else 0
        unique_crane_models = merged_df['TruckCraneID'].nunique() if not merged_df.empty and 'TruckCraneID' in merged_df.columns else 0

        stat_lines.append(f"总计数据行数 (合并后): {total_rows} 行")
        stat_lines.append(f"包含副臂数据的行数: {rows_with_jib} 行")
        stat_lines.append(f"纯主臂数据行数: {total_rows - rows_with_jib} 行")
        stat_lines.append(f"汽车吊型号数量: {unique_crane_models} 个")

        # 主臂工况名称和数据条数 (基于合并后的数据)
        # 检查 SpeWorkCondition 列是否存在且非空
        if not merged_df.empty and 'SpeWorkCondition' in merged_df.columns:
             # 过滤出主臂数据部分，并且 SpeWorkCondition 非空
             main_df_merged = merged_df[(merged_df['IsJibHosCon'] == "否") & (merged_df['SpeWorkCondition'].astype(str).str.strip() != "")].copy() # 创建副本并过滤
             main_names_merged = main_df_merged['SpeWorkCondition'].astype(str).str.strip().unique().tolist() # 获取唯一名称列表
             
             stat_lines.append(f"主臂工况名称个数 (合并后): {len(main_names_merged)}")
             stat_lines.append("主臂工况名称及对应数据条数:")
             if main_names_merged:
                 for name in main_names_merged:
                     count = main_df_merged[main_df_merged['SpeWorkCondition'].astype(str).str.strip() == name].shape[0]
                     stat_lines.append(f"  '{name}': {count} 条") # 加引号避免空格问题
             else:
                  stat_lines.append("  无有效主臂工况数据")
        else:
             stat_lines.append("主臂工况名称个数 (合并后): 0")
             stat_lines.append("主臂工况名称及对应数据条数:\n  无有效主臂工况数据")


        # 副臂工况名称和数据条数 (基于合并后的数据)
        # 检查 SecondSpeWorkCondition 列是否存在且非空
        if not merged_df.empty and 'SecondSpeWorkCondition' in merged_df.columns:
            # 过滤出副臂数据部分，并且 SecondSpeWorkCondition 非空
            jib_df_merged = merged_df[(merged_df['IsJibHosCon'] == "是") & (merged_df['SecondSpeWorkCondition'].astype(str).str.strip() != "")].copy() # 创建副本并过滤
            # 过滤掉空的副臂工况名称
            jib_names_merged = jib_df_merged['SecondSpeWorkCondition'].astype(str).str.strip().unique().tolist() # 获取唯一名称列表

            stat_lines.append(f"主臂+副臂工况名称个数 (合并后): {len(jib_names_merged)}")
            stat_lines.append("主臂+副臂工况名称及对应数据条数:")
            if jib_names_merged:
                for name in jib_names_merged:
                    count = jib_df_merged[jib_df_merged['SecondSpeWorkCondition'].astype(str).str.strip() == name].shape[0]
                    stat_lines.append(f"  '{name}': {count} 条") # 加引号
            else:
                 stat_lines.append("  无有效主臂+副臂工况数据")
        else:
             stat_lines.append("主臂+副臂工况名称个数 (合并后): 0")
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


        # 提醒用户是否打开txt
        if os.path.exists(stat_path) and messagebox.askyesno("统计信息", f"统计信息已保存到:\\n{stat_path}\\n\\n是否现在打开该文件？"):
            import subprocess
            import platform
            try:
                if platform.system() == "Windows":
                    os.startfile(stat_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", stat_path])
                else:
                    subprocess.Popen(["xdg-open", stat_path])
            except FileNotFoundError:
                 messagebox.showerror("错误", f"无法找到打开 {stat_path} 的应用程序。")
            except Exception as open_error:
                 messagebox.showerror("打开文件错误", f"打开文件时发生错误: {open_error}")


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
        main()



if __name__ == "__main__":
    main()

