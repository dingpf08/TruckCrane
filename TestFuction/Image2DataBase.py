#输入的内容：为excel表格，可以有多个相同格式的Excel表格输入：标题格式如下所式：4-(STC250E-1)-(配重6.2t，支腿半伸)_三列_20250515_165052.xlsx
#第一个数字为工况编号，第一个括号()中的内容为汽车吊的名称，第二个括号()中的内容为工况名称，表格第一列（从第二行开始）内容为主臂长，表格第二列（从第二行开始）内容为幅度，表格第三列（从第二行开始）内容为额定吊重
#根据输入内容要输出以下Excel表格：
# 表格第一列为汽车吊的名字，从输入表格标题的第一个括号中解析；表格第二列为工况编号，从输入表格标题开头的数字解析；表格第三列为工况名称，从输入表格标题的第二个括号中解析。
# 表格第四列为幅度，从输入表格内容的第二列（从第二排开始）解析；表格第五列为主臂长，从输入表格内容的第一列（从第二排开始）解析；表格第六列为额定吊重，从输入表格内容的第三列（从第二排开始）解析；

"""
Excel表格数据库转换工具
- 读取三列格式的Excel表格内容（主臂长、调幅、额定吊重）
- 从文件名中提取汽车吊型号、工况编号和工况名称信息
- 将数据重新组织为数据库导入格式
"""

import os
import re
import pandas as pd
from datetime import datetime

# 定义文件夹路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
INPUT_DIR = os.path.join(CURRENT_DIR, 'output_excel')     # 输入Excel文件目录（原脚本的输出目录）
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'database_excel')  # 数据库格式输出目录

# 确保输入输出目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_info_from_filename(filename):
    """
    从文件名中提取汽车吊型号、工况编号和工况名称信息
    
    文件名格式示例: 4-(STC250E-1)-(配重6.2t，支腿半伸)_三列_20250515_165052.xlsx
    
    Args:
        filename (str): 文件名
        
    Returns:
        tuple: (汽车吊型号, 工况编号, 工况名称) 例如 ("STC250E-1", 4, "配重6.2t，支腿半伸")
    """
    try:
        # 提取文件名开头的工况编号
        condition_number_match = re.match(r'^(\d+)-', filename)
        condition_number = int(condition_number_match.group(1)) if condition_number_match else 0
        
        # 使用正则表达式提取括号中的内容
        pattern = r'\(([^)]*)\)'
        matches = re.findall(pattern, filename)
        
        if len(matches) >= 2:
            crane_name = matches[0]    # 第一个括号中的内容为汽车吊型号
            condition_name = matches[1]  # 第二个括号中的内容为工况名称
            return crane_name, condition_number, condition_name
        else:
            print(f"无法从文件名 '{filename}' 中提取信息，格式不符合要求")
            return "未知型号", 0, "未知工况"
    except Exception as e:
        print(f"提取文件名信息时出错: {e}")
        return "未知型号", 0, "未知工况"

def convert_to_database_format(input_file):
    """
    将三列格式的Excel表格转换为数据库导入格式
    
    Args:
        input_file (str): 输入Excel文件路径
        
    Returns:
        DataFrame: 转换后的数据库格式DataFrame，转换失败则返回None
    """
    try:
        # 从文件名中提取汽车吊型号、工况编号和工况名称
        filename = os.path.basename(input_file)
        crane_name, condition_number, condition_name = extract_info_from_filename(filename)
        
        # 读取Excel文件
        df = pd.read_excel(input_file)
        
        # 检查数据有效性
        if df.empty:
            print(f"输入文件 '{filename}' 不包含数据")
            return None
            
        # 检查列名是否符合预期
        expected_columns = ['主臂长(m)', '调幅(m)', '额定吊重(t)']
        # 标准化列名（去除空格，转为小写）以便比较
        actual_columns = [col.strip().lower() for col in df.columns]
        expected_columns_normalized = [col.strip().lower() for col in expected_columns]
        
        # 如果列名不匹配，尝试使用默认列顺序
        if not all(col in actual_columns for col in expected_columns_normalized):
            print(f"警告: 文件 '{filename}' 列名不符合预期，将使用默认列顺序")
            # 假设前三列分别是：主臂长、调幅、额定吊重
            if len(df.columns) >= 3:
                df.columns = expected_columns + list(df.columns[3:])
            else:
                print(f"错误: 文件 '{filename}' 列数不足，无法继续处理")
                return None
        
        # 创建新的DataFrame用于数据库格式
        db_data = []
        
        # 遍历每一行数据
        for _, row in df.iterrows():
            # 创建数据库格式的行
            db_row = [
                crane_name,         # 第一列：汽车吊型号
                condition_number,   # 第二列：工况编号
                condition_name,     # 第三列：工况名称
                row['调幅(m)'],     # 第四列：幅度（从原表第二列获取）
                row['主臂长(m)'],   # 第五列：主臂长（从原表第一列获取）
                row['额定吊重(t)']  # 第六列：额定吊重（从原表第三列获取）
            ]
            db_data.append(db_row)
        
        # 创建数据库格式的DataFrame
        db_df = pd.DataFrame(db_data, columns=[
            '汽车吊型号', '工况编号', '工况名称', '幅度(m)', '主臂长(m)', '额定吊重(t)'
        ])
        
        return db_df
    
    except Exception as e:
        print(f"转换文件 '{input_file}' 时出错: {e}")
        return None

def process_all_excel_files():
    """处理input_dir目录下的所有符合格式的Excel文件"""
    # 获取所有Excel文件
    excel_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print(f"在 {INPUT_DIR} 中未找到Excel文件")
        print("请确保文件名格式为: 工况编号-(型号)-(工况名称)_XXX.xlsx")
        return
    
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    # 合并所有文件的数据
    all_data = []
    
    # 逐个处理Excel文件
    for filename in excel_files:
        input_path = os.path.join(INPUT_DIR, filename)
        print(f"\n开始处理: {filename}")
        
        try:
            # 转换为数据库格式
            db_df = convert_to_database_format(input_path)
            
            if db_df is not None:
                print(f"成功转换: {filename}，包含 {len(db_df)} 行数据")
                all_data.append(db_df)
            else:
                print(f"转换失败: {filename}")
                
        except Exception as e:
            print(f"处理 {filename} 时发生错误: {e}")
    
    # 合并所有数据
    if all_data:
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"汽车吊数据库格式_{timestamp}.xlsx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 保存到Excel
        merged_df.to_excel(output_path, index=False)
        print(f"\n成功生成数据库格式Excel: {output_filename}")
        print(f"总计处理 {len(merged_df)} 行数据")
        return output_path
    else:
        print("\n未能成功转换任何文件，无法生成输出")
        return None

def process_single_file(file_path):
    """
    处理单个Excel文件
    
    Args:
        file_path (str): 要处理的Excel文件路径
        
    Returns:
        str or None: 处理成功则返回输出文件路径，失败则返回None
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
    
    filename = os.path.basename(file_path)
    
    try:
        print(f"\n开始处理: {filename}")
        
        # 转换为数据库格式
        db_df = convert_to_database_format(file_path)
        
        if db_df is not None:
            # 生成输出文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"汽车吊数据库格式_{timestamp}.xlsx"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            # 保存到Excel
            db_df.to_excel(output_path, index=False)
            print(f"成功生成数据库格式Excel: {output_filename}")
            print(f"共处理 {len(db_df)} 行数据")
            return output_path
        else:
            print(f"转换失败: {filename}")
            return None
            
    except Exception as e:
        print(f"处理 {filename} 时发生错误: {e}")
        return None

if __name__ == '__main__':
    print("Excel表格数据库转换工具启动")
    print(f"输入文件夹: {INPUT_DIR}")
    print(f"输出文件夹: {OUTPUT_DIR}")
    
    # 用户交互菜单
    while True:
        print("\n请选择操作:")
        print("1. 处理所有符合格式的Excel文件并合并到一个数据库格式文件")
        print("2. 指定单个Excel文件进行处理")
        print("3. 退出程序")
        
        choice = input("请输入选项(1/2/3): ")
        
        if choice == '1':
            process_all_excel_files()
        elif choice == '2':
            file_path = input("请输入Excel文件的完整路径: ")
            process_single_file(file_path)
        elif choice == '3':
            print("程序结束")
            break
        else:
            print("无效选项，请重新选择")