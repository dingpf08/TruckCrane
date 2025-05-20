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
        return process_jib_excel_file(file_path), truck_crane_id, True

    # 以下是处理主臂工况文件的代码
    try:
        print(f"  - 开始读取文件: {file_path}")
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        if df.empty:
            raise ValueError("Excel文件不包含数据")
        print(f"  - 表格尺寸: {df.shape[0]}行 x {df.shape[1]}列")
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
        return result_df, truck_crane_id, False
    except Exception as e:
        raise ValueError(f"处理文件 '{file_path}' 时出错: {str(e)}")

def process_multiple_files(file_paths):
    """
    处理多个Excel文件并合并结果
    
    Args:
        file_paths (list): Excel文件路径列表
        
    Returns:
        tuple: (合并的DataFrame, 汽车吊型号列表)
    """
    if not file_paths:
        raise ValueError("没有选择文件")
        
    main_data = []  # 存储主臂工况数据
    jib_data = []   # 存储副臂工况数据
    truck_crane_ids = set()
    processed_count = 0
    error_count = 0
    
    for file_path in file_paths:
        try:
            print(f"\n处理文件: {os.path.basename(file_path)}")
            df, truck_crane_id, is_jib = process_excel_file(file_path)
            
            # 根据文件类型分别存储数据
            if is_jib:
                jib_data.append(df)
            else:
                main_data.append(df)
                
            truck_crane_ids.add(truck_crane_id)
            processed_count += 1
            print(f"  - 成功处理: {len(df)} 行数据")
        except Exception as e:
            error_count += 1
            print(f"  - 错误: {str(e)}")
    
    # 打印处理统计
    print(f"\n处理统计:")
    print(f"  - 成功处理: {processed_count} 个文件")
    print(f"  - 处理失败: {error_count} 个文件")
    
    if not main_data and not jib_data:
        raise ValueError("所有文件处理失败")
    
    # 首先处理主臂工况数据
    if main_data:
        merged_main_df = pd.concat(main_data, ignore_index=True)
    else:
        # 如果没有主臂工况数据，则无法继续处理
        raise ValueError("未找到有效的主臂工况数据，必须至少有一个主臂工况文件")
    
    # 处理副臂工况数据
    if jib_data:
        merged_jib_df = pd.concat(jib_data, ignore_index=True)
    else:
        merged_jib_df = pd.DataFrame()
    
    # 确保所有必要的列都存在于主臂工况数据中
    required_columns = [
        'TruckCraneID', 'ConditionID', 'SpeWorkCondition', 
        'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap',
        'IsJibHosCon', 'SecondSpeWorkCondition', 'SecondElevation',
        'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap'
    ]
    
    # 添加缺失的列
    for col in required_columns:
        if col not in merged_main_df.columns:
            if col == 'IsJibHosCon':
                merged_main_df[col] = "否"  # 默认为非副臂工况
            else:
                merged_main_df[col] = 0 if col not in ['TruckCraneID', 'SpeWorkCondition', 'SecondSpeWorkCondition'] else ""
    
    # 按照汽车吊型号、工况名称、主臂长、幅度排序主臂工况数据
    merged_main_df = merged_main_df.sort_values(by=[
        'TruckCraneID',
        'SpeWorkCondition',
        'TruckCraneMainArmLen',
        'TruckCraneRange'
    ]).reset_index(drop=True)
    
    # 如果有副臂工况数据，按顺序填入主臂工况数据
    if not merged_jib_df.empty:
        print("\n填入副臂工况数据...")
        
        # 对每个汽车吊型号处理
        for crane_id in truck_crane_ids:
            # 获取该型号的主臂工况数据
            crane_main_df = merged_main_df[merged_main_df['TruckCraneID'] == crane_id]
            
            if crane_main_df.empty:
                print(f"  - 警告: 没有找到型号 {crane_id} 的主臂工况数据")
                continue
                
            # 获取该型号的副臂工况数据
            crane_jib_df = merged_jib_df[merged_jib_df['TruckCraneID'] == crane_id]
            
            if crane_jib_df.empty:
                print(f"  - 信息: 没有找到型号 {crane_id} 的副臂工况数据")
                continue
                
            # 获取该型号主臂工况的索引
            main_indices = crane_main_df.index
            
            # 按顺序填入副臂工况数据（只填充有数据的部分，不足的保持空白）
            filled_count = 0
            for i, (_, jib_row) in enumerate(crane_jib_df.iterrows()):
                if i < len(main_indices):
                    main_idx = main_indices[i]
                    
                    # 将副臂工况信息填入主臂工况行
                    merged_main_df.at[main_idx, 'IsJibHosCon'] = "是"
                    merged_main_df.at[main_idx, 'SecondSpeWorkCondition'] = jib_row['SecondSpeWorkCondition']
                    merged_main_df.at[main_idx, 'SecondElevation'] = jib_row['SecondElevation']
                    merged_main_df.at[main_idx, 'SecondMainArmLen'] = jib_row['SecondMainArmLen']
                    merged_main_df.at[main_idx, 'SecondTruckCraneRatedLiftingCap'] = jib_row['SecondTruckCraneRatedLiftingCap']
                    filled_count += 1
            
            print(f"  - 成功为型号 {crane_id} 填入 {filled_count} 行副臂工况数据 (共 {len(crane_main_df)} 行主臂数据)")
    
    # 最终结果就是处理后的主臂工况数据（已包含副臂信息）
    return merged_main_df, list(truck_crane_ids)

def main():
    """主函数：提供文件选择界面并处理选择的文件"""
    root = tk.Tk()
    root.title("汽车吊数据转换工具")
    root.withdraw()  # 隐藏主窗口

    print("原始Excel转数据库格式工具")
    print("============================\n")
    print("本工具可以一次性处理主臂吊装工况和主臂+副臂工况的Excel文件")
    print("文件名格式要求:")
    print("  - 主臂工况格式: 工况编号-(汽车吊型号)-(工况名称).xlsx")
    print("  - 副臂工况格式: (汽车吊型号)-(工况名称).xlsx")
    print("============================\n")
    print("请选择要处理的Excel文件(可同时选择主臂工况和主臂+副臂工况文件)...")

    file_paths = filedialog.askopenfilenames(
        title="选择需要处理的Excel文件 (主臂工况和主臂+副臂工况)",
        filetypes=[("Excel文件", "*.xlsx *.xls")]
    )

    if not file_paths:
        print("未选择任何文件，程序退出")
        return

    # 分类统计
    main_files = []
    jib_files = []
    error_files = []
    for file_path in file_paths:
        try:
            file_name = os.path.basename(file_path)
            _, _, _, is_jib, _ = extract_info_from_filename(file_name)
            if is_jib:
                jib_files.append(file_name)
            else:
                main_files.append(file_name)
        except Exception as e:
            error_files.append(f"{file_name} (无法识别: {e})")

    # 弹窗提醒
    msg = "文件分类如下：\n\n"
    msg += f"主臂工况Excel表格 ({len(main_files)} 个):\n" + ("\n".join(main_files) if main_files else "无") + "\n\n"
    msg += f"主臂+副臂工况Excel表格 ({len(jib_files)} 个):\n" + ("\n".join(jib_files) if jib_files else "无") + "\n\n"
    if error_files:
        msg += f"无法识别的文件 ({len(error_files)} 个):\n" + ("\n".join(error_files)) + "\n\n"
    messagebox.showinfo("文件类型分类", msg)

    try:
        print(f"选择了 {len(file_paths)} 个文件")
        merged_df, truck_crane_ids = process_multiple_files(file_paths)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if len(truck_crane_ids) == 1:
            base_name = f"{truck_crane_ids[0]}-额定起重量表-{timestamp}.xlsx"
        else:
            base_name = f"多种汽车吊-额定起重量表-{timestamp}.xlsx"
        output_dir = os.path.dirname(file_paths[0])
        output_path = os.path.join(output_dir, base_name)
        merged_df.to_excel(output_path, index=False)
        total_rows = len(merged_df)
        rows_with_jib = merged_df[merged_df['IsJibHosCon'] == "是"].shape[0]
        unique_crane_models = len(truck_crane_ids)
        unique_work_conditions = merged_df['SpeWorkCondition'].nunique()
        model_stats = []
        for model in truck_crane_ids:
            model_data = merged_df[merged_df['TruckCraneID'] == model]
            total_rows_model = len(model_data)
            rows_with_jib_model = model_data[model_data['IsJibHosCon'] == "是"].shape[0]
            model_stats.append(f"  - {model}: 共 {total_rows_model} 行, 其中 {rows_with_jib_model} 行包含副臂数据")
        print(f"\n处理完成!")
        print(f"总计处理 {total_rows} 行数据")
        print(f"  - 包含副臂数据的行数: {rows_with_jib} 行")
        print(f"汽车吊型号数量: {unique_crane_models} 个")
        print(f"不同工况数量: {unique_work_conditions} 个")
        print(f"按型号统计:")
        for stat in model_stats:
            print(stat)
        print(f"输出文件: {output_path}")
        messagebox.showinfo("处理完成", \
            f"成功处理 {len(file_paths)} 个文件\n\n" +
            f"总计数据: {total_rows} 行\n" +
            f"  - 包含副臂数据的行数: {rows_with_jib} 行\n\n" +
            f"汽车吊型号: {unique_crane_models} 个\n" +
            f"不同工况: {unique_work_conditions} 个\n\n" +
            f"输出文件: {os.path.basename(output_path)}")
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(f"\n错误: {error_msg}")
        messagebox.showerror("处理错误", error_msg)
    if messagebox.askyesno("操作完成", "是否关闭程序?"):
        root.destroy()
    else:
        main()  # 重新启动处理流程

def process_jib_excel_file(file_path):
    """
    处理主臂+副臂工况的Excel文件
    假设每组三列为一个工况，第一行为工况名，第二行为幅度，第三行及以后为仰角和额定吊重
    """
    file_name = os.path.basename(file_path)
    truck_crane_id, _, _, is_jib, jib_condition = extract_info_from_filename(file_name)
    if not is_jib:
        raise ValueError(f"文件 '{file_name}' 不是主臂+副臂工况文件")
    try:
        print(f"  - 开始读取主臂+副臂工况文件: {file_path}")
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        if df.empty:
            raise ValueError("Excel文件不包含数据")
        print(f"  - 表格尺寸: {df.shape[0]}行 x {df.shape[1]}列")
        if df.shape[0] < 4 or df.shape[1] < 4:
            raise ValueError("主臂+副臂工况表格至少需要4行4列")
        results = []
        # 假设每组三列为一个工况
        group_size = 3
        n_groups = (df.shape[1] - 1) // group_size
        for g in range(n_groups):
            col_start = 1 + g * group_size
            col_end = col_start + group_size
            # 工况名
            jib_condition_name = str(df.iloc[0, col_start])
            # 幅度
            group_ranges = [df.iloc[1, col_start + k] for k in range(group_size)]
            # 遍历仰角行
            for row in range(2, df.shape[0]):
                elevation = df.iloc[row, col_start]
                if pd.isna(elevation):
                    continue
                try:
                    if isinstance(elevation, str):
                        clean_val = ''.join(c for c in elevation if c.isdigit() or c == '.' or c == '-')
                        elevation = float(clean_val) if clean_val else None
                    else:
                        elevation = float(elevation)
                except:
                    continue
                for k, group_range in enumerate(group_ranges):
                    lifting_cap = df.iloc[row, col_start + k]
                    if pd.isna(lifting_cap):
                        continue
                    try:
                        if isinstance(lifting_cap, str):
                            clean_val = ''.join(c for c in lifting_cap if c.isdigit() or c == '.' or c == '-')
                            lifting_cap = float(clean_val) if clean_val else None
                        else:
                            lifting_cap = float(lifting_cap)
                    except:
                        continue
                    if lifting_cap is None or lifting_cap <= 0:
                        continue
                    results.append({
                        'TruckCraneID': truck_crane_id,
                        'ConditionID': None,
                        'SpeWorkCondition': None,
                        'TruckCraneRange': group_range,
                        'TruckCraneMainArmLen': 0,
                        'TruckCraneRatedLiftingCap': 0,
                        'IsJibHosCon': "是",
                        'SecondSpeWorkCondition': jib_condition_name,
                        'SecondElevation': elevation,
                        'SecondMainArmLen': 0,
                        'SecondTruckCraneRatedLiftingCap': lifting_cap
                    })
        result_df = pd.DataFrame(results)
        if result_df.empty:
            raise ValueError("未能从主臂+副臂工况文件中提取有效数据")
        return result_df
    except Exception as e:
        raise ValueError(f"处理主臂+副臂工况文件 '{file_path}' 时出错: {str(e)}")

if __name__ == "__main__":
    main()

