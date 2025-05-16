#输入的文件为Excel表格，表格标题和内容的格式如下：
#标题格式：1-(STC250E-1)-(配重6.2t，支腿全伸).xlsx 其中1代表工况编号，第一个括号的内容：STC250E-1代表汽车吊型号，第二个括号的内容"配重6.2t，支腿全伸"代表工况名称
#内容格式：输入的Excel表格内容中：第一行（除了第一行第一列单元格）内容代表汽车吊主臂长，第一列（除了第一行第一列单元格）内容代表汽车吊幅度，行和列交叉的单元格代表汽车吊额定吊重

#输出的Excel文件内容：
#第一行标题列分别为：TruckCraneID，ConditionID，SpeWorkCondition，TruckCraneRange，TruckCraneMainArmLen，TruckCraneRatedLiftingCap
        #分别代表：汽车吊型号，工况编号，工况名称，汽车吊幅度，汽车吊主臂长，汽车吊额定吊重
#其他行分别为输入文件中对应的内容，其中排列顺序为：首先按照汽车吊型号排序，然后按照工况编号排序，然后按照工况名称排序，然后按照汽车吊主臂长排序，然后按照汽车吊幅度排序，最后按照汽车吊额定吊重排序

#输入Excel表格时候  让用户自己选择对应文件夹下的Excel表格，可以单选也可以多选，输出Excel文件的时候 默认输出到输入文件的目录下，输出文件的标题格式为 汽车吊名称-额定起重量表-当前时间戳.xlsx

"""
原始Excel转数据库格式工具

本工具用于将交叉表格式(二维表)的起重机数据转换为数据库友好的行格式。

输入格式:
- 文件名格式：工况编号-(型号)-(工况名称).xlsx
- 表格格式：第一行为主臂长，第一列为幅度，交叉单元格为额定吊重

输出格式:
- 六列数据库格式：汽车吊型号，工况编号，工况名称，汽车吊幅度，汽车吊主臂长，汽车吊额定吊重
- 按照特定顺序排序
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
    
    Args:
        file_path (str): Excel文件路径
        
    Returns:
        tuple: (DataFrame, 汽车吊型号)
    """
    # 从文件名提取信息
    file_name = os.path.basename(file_path)
    truck_crane_id, condition_id, work_condition, is_jib, jib_condition = extract_info_from_filename(file_name)
    
    # 根据文件名判断是否为副臂工况文件
    if is_jib:
        # 如果是副臂工况文件，使用专门的处理函数
        return process_jib_excel_file(file_path), truck_crane_id
    
    # 以下是处理主臂工况文件的代码
    try:
        # 添加详细打印以便调试
        print(f"  - 开始读取文件: {file_path}")
        
        # 读取Excel文件，明确指定引擎和参数
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        
        if df.empty:
            raise ValueError("Excel文件不包含数据")

        # 打印表格尺寸以便调试
        print(f"  - 表格尺寸: {df.shape[0]}行 x {df.shape[1]}列")
        
        # 检查数据格式
        if df.shape[0] < 2 or df.shape[1] < 2:
            raise ValueError("Excel表格至少需要2行2列")
            
        # 获取主臂长数据（从第一行，跳过第一个单元格）
        arm_lengths = df.iloc[0, 1:].values
        
        # 数据清理 - 确保主臂长数据是有效的数字
        clean_arm_lengths = []
        for i, val in enumerate(arm_lengths):
            try:
                # 尝试转换为浮点数，移除任何非数字字符
                if pd.isna(val):
                    continue
                
                # 如果是字符串，清理并转换
                if isinstance(val, str):
                    # 移除所有非数字和小数点
                    clean_val = ''.join(c for c in val if c.isdigit() or c == '.')
                    if clean_val:
                        clean_arm_lengths.append((i, float(clean_val)))
                else:
                    # 直接转换数值
                    clean_arm_lengths.append((i, float(val)))
            except Exception as e:
                print(f"Warning: 无法解析主臂长值 '{val}' 在列 {i+1}: {str(e)}")
        
        if not clean_arm_lengths:
            raise ValueError("未能提取到有效的主臂长数据")
        
        # 获取幅度数据（从第一列，跳过第一个单元格）
        ranges = df.iloc[1:, 0].values
        
        # 数据清理 - 确保幅度数据是有效的数字
        clean_ranges = []
        for i, val in enumerate(ranges):
            try:
                # 尝试转换为浮点数，移除任何非数字字符
                if pd.isna(val):
                    continue
                
                # 如果是字符串，清理并转换
                if isinstance(val, str):
                    # 移除所有非数字和小数点
                    clean_val = ''.join(c for c in val if c.isdigit() or c == '.')
                    if clean_val:
                        clean_ranges.append((i, float(clean_val)))
                else:
                    # 直接转换数值
                    clean_ranges.append((i, float(val)))
            except Exception as e:
                print(f"Warning: 无法解析幅度值 '{val}' 在行 {i+2}: {str(e)}")
        
        if not clean_ranges:
            raise ValueError("未能提取到有效的幅度数据")
        
        # 创建结果列表
        results = []
        
        # 遍历数据区域 - 使用清理后的索引和值
        for range_idx, range_val in clean_ranges:
            for arm_idx, arm_len in clean_arm_lengths:
                try:
                    # 获取额定吊重值（range_idx+1行，arm_idx+1列）
                    lifting_cap = df.iloc[range_idx+1, arm_idx+1]
                    
                    # 检查额定吊重是否为有效值
                    if pd.isna(lifting_cap):
                        continue
                    
                    # 如果是字符串，尝试清理并转换
                    if isinstance(lifting_cap, str):
                        # 清理字符串
                        lifting_cap = lifting_cap.strip()
                        if not lifting_cap:
                            continue
                        
                        # 移除所有非数字和小数点
                        clean_val = ''.join(c for c in lifting_cap if c.isdigit() or c == '.')
                        if not clean_val:
                            continue
                        
                        try:
                            lifting_cap = float(clean_val)
                        except:
                            print(f"Warning: 无法将值 '{lifting_cap}' 转换为数字，跳过 (行={range_idx+2}, 列={arm_idx+2})")
                            continue
                    else:
                        # 直接转换数值
                        try:
                            lifting_cap = float(lifting_cap)
                        except:
                            print(f"Warning: 无法将值 '{lifting_cap}' 转换为数字，跳过 (行={range_idx+2}, 列={arm_idx+2})")
                            continue
                    
                    # 跳过0或负值，通常代表不可吊装
                    if lifting_cap <= 0:
                        continue
                    
                    # 添加到结果列表，包含新增的列
                    results.append({
                        'TruckCraneID': truck_crane_id,  # 汽车吊型号
                        'ConditionID': condition_id,    # 工况编号
                        'SpeWorkCondition': work_condition,  # 工况名称
                        'TruckCraneRange': range_val,   # 幅度
                        'TruckCraneMainArmLen': arm_len,  # 主臂长
                        'TruckCraneRatedLiftingCap': lifting_cap,  # 额定吊重
                        'IsJibHosCon': "否",  # 标记为主臂工况
                        'SecondSpeWorkCondition': "",  # 副臂工况名称留空
                        'SecondElevation': 0,  # 仰角留空
                        'SecondMainArmLen': 0,  # 主臂+副臂主臂长留空
                        'SecondTruckCraneRatedLiftingCap': 0  # 主臂+副臂额定吊重留空
                    })
                except Exception as e:
                    print(f"Warning: 处理数据时出错 (行={range_idx+2}, 列={arm_idx+2}): {str(e)}")
        
        # 创建数据库格式的DataFrame
        result_df = pd.DataFrame(results)
        
        # 如果结果为空，抛出错误
        if result_df.empty:
            raise ValueError("无法从Excel提取有效数据")
            
        return result_df, truck_crane_id
        
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
        
    all_data = []
    truck_crane_ids = set()
    processed_count = 0
    error_count = 0
    
    for file_path in file_paths:
        try:
            print(f"\n处理文件: {os.path.basename(file_path)}")
            df, truck_crane_id = process_excel_file(file_path)
            all_data.append(df)
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
    
    if not all_data:
        raise ValueError("所有文件处理失败")
        
    # 合并所有数据帧
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # 确保所有必要的列都存在
    required_columns = [
        'TruckCraneID', 'ConditionID', 'SpeWorkCondition', 
        'TruckCraneRange', 'TruckCraneMainArmLen', 'TruckCraneRatedLiftingCap',
        'IsJibHosCon', 'SecondSpeWorkCondition', 'SecondElevation',
        'SecondMainArmLen', 'SecondTruckCraneRatedLiftingCap'
    ]
    
    # 添加缺失的列
    for col in required_columns:
        if col not in merged_df.columns:
            if col == 'IsJibHosCon':
                merged_df[col] = "否"  # 默认为非副臂工况
            else:
                merged_df[col] = 0 if col not in ['TruckCraneID', 'SpeWorkCondition', 'SecondSpeWorkCondition'] else ""
    
    # 按照要求排序
    merged_df = merged_df.sort_values(by=[
        'TruckCraneID', 
        'ConditionID', 
        'SpeWorkCondition', 
        'TruckCraneMainArmLen', 
        'TruckCraneRange', 
        'TruckCraneRatedLiftingCap'
    ])
    
    return merged_df, list(truck_crane_ids)

def main():
    """主函数：提供文件选择界面并处理选择的文件"""
    # 创建简单的Tkinter根窗口
    root = tk.Tk()
    root.title("汽车吊数据转换工具")
    root.withdraw()  # 隐藏主窗口
    
    print("原始Excel转数据库格式工具")
    print("============================\n")
    print("本工具可以一次性处理主臂吊装工况和主臂+副臂吊装工况的Excel文件")
    print("文件名格式要求:")
    print("  - 主臂工况格式: 工况编号-(汽车吊型号)-(工况名称).xlsx")
    print("  - 副臂工况格式: (汽车吊型号)-(工况名称).xlsx")
    print("============================\n")
    print("请选择要处理的Excel文件(可同时选择主臂工况和主臂+副臂工况文件)...")
    
    # 打开文件选择对话框
    file_paths = filedialog.askopenfilenames(
        title="选择需要处理的Excel文件 (主臂工况和主臂+副臂工况)",
        filetypes=[("Excel文件", "*.xlsx *.xls")]
    )
    
    if not file_paths:
        print("未选择任何文件，程序退出")
        return
    
    try:
        # 处理选定的文件
        print(f"选择了 {len(file_paths)} 个文件")
        merged_df, truck_crane_ids = process_multiple_files(file_paths)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 如果所有文件都是同一个汽车吊，则使用其名称
        if len(truck_crane_ids) == 1:
            base_name = f"{truck_crane_ids[0]}-额定起重量表-{timestamp}.xlsx"
        else:
            # 否则使用通用名称
            base_name = f"多种汽车吊-额定起重量表-{timestamp}.xlsx"
        
        # 默认输出到第一个输入文件的目录
        output_dir = os.path.dirname(file_paths[0])
        output_path = os.path.join(output_dir, base_name)
        
        # 保存转换后的数据
        merged_df.to_excel(output_path, index=False)
        
        print(f"\n处理完成!")
        print(f"总计处理 {len(merged_df)} 行数据")
        print(f"输出文件: {output_path}")
        
        # 打印工况类型统计
        main_conditions = merged_df[merged_df['IsJibHosCon'] == "否"].shape[0]
        jib_conditions = merged_df[merged_df['IsJibHosCon'] == "是"].shape[0]
        print(f"  - 主臂工况数据: {main_conditions} 行")
        print(f"  - 主臂+副臂工况数据: {jib_conditions} 行")
        
        # 显示成功消息
        messagebox.showinfo("处理完成", 
            f"成功处理 {len(file_paths)} 个文件，共 {len(merged_df)} 行数据\n" +
            f"  - 主臂工况数据: {main_conditions} 行\n" +
            f"  - 主臂+副臂工况数据: {jib_conditions} 行\n\n" +
            f"输出文件: {os.path.basename(output_path)}")
            
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(f"\n错误: {error_msg}")
        messagebox.showerror("处理错误", error_msg)
        
    # 让用户决定是否继续
    if messagebox.askyesno("操作完成", "是否关闭程序?"):
        root.destroy()
    else:
        main()  # 重新启动处理流程

def process_jib_excel_file(file_path):
    """
    处理主臂+副臂工况的Excel文件
    
    文件格式：第一行第二列的单元格是主臂长，第一列是仰角，第二列是对应的主臂+副臂额定吊重
    
    Args:
        file_path (str): Excel文件路径
        
    Returns:
        DataFrame: 处理后的数据帧
    """
    # 从文件名提取信息
    file_name = os.path.basename(file_path)
    truck_crane_id, _, _, is_jib, jib_condition = extract_info_from_filename(file_name)
    
    if not is_jib:
        raise ValueError(f"文件 '{file_name}' 不是主臂+副臂工况文件")
    
    try:
        # 添加详细打印以便调试
        print(f"  - 开始读取主臂+副臂工况文件: {file_path}")
        
        # 读取Excel文件
        df = pd.read_excel(file_path, header=None, engine='openpyxl')
        
        if df.empty:
            raise ValueError("Excel文件不包含数据")
            
        # 打印表格尺寸以便调试
        print(f"  - 表格尺寸: {df.shape[0]}行 x {df.shape[1]}列")
        
        # 检查数据格式
        if df.shape[0] < 2 or df.shape[1] < 2:
            raise ValueError("Excel表格至少需要2行2列")
            
        # 获取主臂长 - 从第一行第二列单元格
        try:
            main_arm_len = df.iloc[0, 1]
            if pd.isna(main_arm_len):
                raise ValueError("第一行第二列(主臂长)不能为空")
                
            main_arm_len = float(main_arm_len)
            print(f"  - 检测到主臂长: {main_arm_len}m")
        except (ValueError, TypeError) as e:
            raise ValueError(f"无法解析主臂长数值: {str(e)}")
            
        # 获取仰角列表 - 从第一列（从第二行开始）
        elevations = []
        for i in range(1, df.shape[0]):
            val = df.iloc[i, 0]
            if pd.notna(val):
                try:
                    if isinstance(val, str):
                        # 清理字符串值，去除可能的单位等
                        clean_val = ''.join(c for c in val if c.isdigit() or c == '.' or c == '-')
                        elevation = float(clean_val) if clean_val else None
                    else:
                        elevation = float(val)
                        
                    if elevation is not None:
                        elevations.append((i, elevation))
                except Exception as e:
                    print(f"  - 警告: 无法解析仰角值 {val} 在行 {i+1}: {str(e)}")
        
        if not elevations:
            raise ValueError("未能提取到有效的仰角数据")
            
        print(f"  - 检测到 {len(elevations)} 个有效仰角值")
        
        # 处理额定吊重数据
        results = []
        for idx, elevation in elevations:
            try:
                # 获取对应行的额定吊重（第二列）
                lifting_cap = df.iloc[idx, 1]
                
                # 检查是否有效
                if pd.isna(lifting_cap):
                    continue
                    
                # 处理字符串值
                if isinstance(lifting_cap, str):
                    lifting_cap = lifting_cap.strip()
                    if not lifting_cap:
                        continue
                    
                    # 清理字符串，去除非数字字符
                    clean_val = ''.join(c for c in lifting_cap if c.isdigit() or c == '.' or c == '-')
                    if not clean_val:
                        continue
                        
                    try:
                        lifting_cap = float(clean_val)
                    except:
                        print(f"  - 警告: 无法将值 '{lifting_cap}' 转换为数字，在行 {idx+1}")
                        continue
                else:
                    try:
                        lifting_cap = float(lifting_cap)
                    except:
                        print(f"  - 警告: 无法将值 '{lifting_cap}' 转换为数字，在行 {idx+1}")
                        continue
                
                # 跳过0或负值
                if lifting_cap <= 0:
                    continue
                    
                # 添加到结果列表
                # 主臂+副臂工况数据使用新增列
                results.append({
                    'TruckCraneID': truck_crane_id,
                    'ConditionID': 0,  # 默认值，可以根据需要调整
                    'SpeWorkCondition': "",  # 主臂工况留空
                    'TruckCraneRange': 0,  # 主臂幅度留空
                    'TruckCraneMainArmLen': 0,  # 主臂长留空
                    'TruckCraneRatedLiftingCap': 0,  # 主臂额定吊重留空
                    'IsJibHosCon': "是",  # 标记为副臂工况
                    'SecondSpeWorkCondition': jib_condition,  # 主臂+副臂工况名称
                    'SecondElevation': elevation,  # 仰角
                    'SecondMainArmLen': main_arm_len,  # 主臂+副臂工况下的主臂长
                    'SecondTruckCraneRatedLiftingCap': lifting_cap  # 主臂+副臂额定吊重
                })
            except Exception as e:
                print(f"  - 警告: 处理主臂+副臂数据时出错 (行={idx+1}): {str(e)}")
                
        # 创建结果数据帧
        result_df = pd.DataFrame(results)
        
        if result_df.empty:
            raise ValueError("未能从主臂+副臂工况文件中提取有效数据")
            
        return result_df
        
    except Exception as e:
        raise ValueError(f"处理主臂+副臂工况文件 '{file_path}' 时出错: {str(e)}")

if __name__ == "__main__":
    main()

