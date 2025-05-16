"""
输入Excel表格EA的标题和内容格式如下：
EA的标题:
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime

# 定义文件夹路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
INPUT_DIR = os.path.join(CURRENT_DIR, 'input_excel')      # 输入Excel文件目录
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'output_excel')    # 输出Excel文件目录

# 确保输入输出目录存在，如果不存在则创建
os.makedirs(INPUT_DIR, exist_ok=True)   # exist_ok=True表示如果目录已存在则不报错
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 创建输出目录

def convert_excel_to_three_columns(input_file):
    """
    将Excel表格数据转换为三列格式
    
    表格格式要求：
    - 第一行（从第二列开始）: 主臂长度值
    - 第一列（从第二行开始）: 调幅值
    - 其他单元格: 对应主臂长和调幅下的额定吊重
    
    Args:
        input_file (str): Excel文件路径
        
    Returns:
        DataFrame: 转换后的三列数据（主臂长、调幅、额定吊重），如果转换失败则返回None
    """
    try:
        # 读取Excel文件，不使用表头
        df = pd.read_excel(input_file, header=None)
        
        # 检查数据是否有效（至少需要2行2列的数据）
        if df.empty or df.shape[0] < 2 or df.shape[1] < 2:
            print(f"表格数据不足，无法转换：{input_file}")
            return None
        
        # 提取主臂长（第一行，从第二列开始）
        arm_lengths = df.iloc[0, 1:].values  # iloc[0, 1:]表示第一行，从第二列开始
        
        # 提取调幅（第一列，从第二行开始）
        radii = df.iloc[1:, 0].values  # iloc[1:, 0]表示从第二行开始，第一列
        
        # 创建结果列表，用于存储转换后的三列数据
        three_columns_data = []
        
        # 遍历每个调幅和主臂长组合，提取对应的额定吊重
        for i, radius in enumerate(radii):
            for j, arm_length in enumerate(arm_lengths):
                # 获取额定吊重值（如果存在）
                # 注意：实际数据位置是第i+1行（因为第一行是主臂长），第j+1列（因为第一列是调幅）
                if j+1 < df.shape[1] and i+1 < df.shape[0]:
                    lifting_capacity = df.iloc[i+1, j+1]
                    
                    # 检查值是否为空或NaN
                    if pd.notna(lifting_capacity) and lifting_capacity != "":
                        # 将值转换为浮点数（如果可能）
                        try:
                            # 转换主臂长、调幅和吊重为数值
                            arm_length_val = float(arm_length) if pd.notna(arm_length) else 0
                            radius_val = float(radius) if pd.notna(radius) else 0
                            capacity_val = float(lifting_capacity) if pd.notna(lifting_capacity) else 0
                            
                            # 添加到结果列表
                            three_columns_data.append([arm_length_val, radius_val, capacity_val])
                        except (ValueError, TypeError):
                            # 如果无法转换为浮点数，则保留原始值并发出警告
                            print(f"警告：无法转换值为数字: 臂长={arm_length}, 调幅={radius}, 吊重={lifting_capacity}")
                            three_columns_data.append([arm_length, radius, lifting_capacity])
        
        # 创建DataFrame并按主臂长和调幅排序
        if three_columns_data:
            # 创建DataFrame，设置列名
            result_df = pd.DataFrame(three_columns_data, columns=['主臂长(m)', '调幅(m)', '额定吊重(t)'])
            # 按主臂长排序，相同主臂长的数据放在一起，再按调幅排序
            result_df = result_df.sort_values(by=['主臂长(m)', '调幅(m)'])
            return result_df
        else:
            print(f"无法从表格中提取有效数据：{input_file}")
            return None
    
    except Exception as e:
        # 捕获并打印所有异常
        print(f"处理Excel文件时出错: {e}")
        return None

def process_all_excel_files():
    """
    批量处理input_excel目录下的所有Excel文件
    
    遍历input_excel目录中的所有.xlsx和.xls文件，将每个文件转换为三列格式并保存
    """
    # 获取所有Excel文件
    excel_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.xlsx', '.xls'))]
    
    # 检查是否有Excel文件
    if not excel_files:
        print(f"在 {INPUT_DIR} 中未找到Excel文件")
        print("请将Excel文件放入该目录后重新运行程序")
        return
    
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    # 逐个处理Excel文件
    for filename in excel_files:
        input_path = os.path.join(INPUT_DIR, filename)
        print(f"\n开始处理: {filename}")
        
        try:
            # 转换为三列格式
            three_columns_df = convert_excel_to_three_columns(input_path)
            
            if three_columns_df is not None:
                # 生成输出文件名（原文件名_三列_时间戳.xlsx）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = os.path.splitext(filename)[0] + f"_三列_{timestamp}.xlsx"
                output_path = os.path.join(OUTPUT_DIR, output_filename)
                
                # 保存到Excel
                three_columns_df.to_excel(output_path, index=False)
                print(f"成功转换并保存到: {output_filename}")
                print(f"共处理 {len(three_columns_df)} 行数据")
            else:
                print(f"转换失败: {filename}")
                
        except Exception as e:
            print(f"处理 {filename} 时发生错误: {e}")

def process_single_file(file_path):
    """
    处理单个Excel文件
    
    Args:
        file_path (str): 要处理的Excel文件路径
        
    Returns:
        str or None: 处理成功则返回输出文件路径，失败则返回None
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    try:
        print(f"\n开始处理: {os.path.basename(file_path)}")
        
        # 转换为三列格式
        three_columns_df = convert_excel_to_three_columns(file_path)
        
        if three_columns_df is not None:
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.splitext(os.path.basename(file_path))[0] + f"_三列_{timestamp}.xlsx"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            # 保存到Excel
            three_columns_df.to_excel(output_path, index=False)
            print(f"成功转换并保存到: {output_filename}")
            print(f"共处理 {len(three_columns_df)} 行数据")
            return output_path
        else:
            print(f"转换失败: {file_path}")
            return None
            
    except Exception as e:
        print(f"处理 {file_path} 时发生错误: {e}")
        return None

if __name__ == '__main__':
    # 程序入口
    print("Excel表格数据转换工具启动")
    print(f"输入文件夹: {INPUT_DIR}")
    print(f"输出文件夹: {OUTPUT_DIR}")
    
    # 用户交互菜单
    while True:
        print("\n请选择操作:")
        print("1. 处理input_excel目录下的所有Excel文件")
        print("2. 指定单个Excel文件进行处理")
        print("3. 退出程序")
        
        choice = input("请输入选项(1/2/3): ")
        
        if choice == '1':
            # 批量处理目录下所有Excel文件
            process_all_excel_files()
        elif choice == '2':
            # 处理单个指定的Excel文件
            file_path = input("请输入Excel文件的完整路径: ")
            process_single_file(file_path)
        elif choice == '3':
            # 退出程序
            print("程序结束")
            break
        else:
            # 无效选项
            print("无效选项，请重新选择")