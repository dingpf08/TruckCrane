"""
图片批量表格识别并导出为Excel
- 遍历 input_images 文件夹下所有图片（JPG, PNG, BMP）
- 对每张图片进行表格识别（OpenCV + pytesseract）
- 识别结果以纯文本表格保存为 Excel，输出到 output_excel 文件夹
- 尽量还原图片表格结构和内容
"""
import os
import cv2
import numpy as np
import pandas as pd
import pytesseract
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
import time
import threading
import concurrent.futures
from datetime import datetime

# 支持的图片格式
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp')

# 文件夹路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(CURRENT_DIR, 'input_images')
OUTPUT_DIR = os.path.join(CURRENT_DIR, 'output_excel')
DEBUG_DIR = os.path.join(CURRENT_DIR, 'debug_images')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

# OCR超时设置（秒）
OCR_TIMEOUT = 3

def enhance_image(img):
    """增强图像，提高对比度和清晰度"""
    # 转换为PIL图像进行增强
    pil_img = Image.fromarray(img)
    
    # 增强对比度
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(2.0)  # 增强对比度2倍
    
    # 增强锐度
    enhancer = ImageEnhance.Sharpness(pil_img)
    pil_img = enhancer.enhance(2.0)  # 增强锐度2倍
    
    # 转回OpenCV格式
    return np.array(pil_img)

def detect_table_structure(img, debug_base, debug=True):
    """检测表格结构，返回行和列的位置"""
    h, w = img.shape[:2]
    
    # 转为灰度图
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_2_gray.jpg"), gray)
    
    # 增强图像
    enhanced = enhance_image(gray)
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_3_enhanced.jpg"), enhanced)
    
    # 自适应二值化 - 更好地处理不同亮度和对比度的图像
    binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_4_binary.jpg"), binary)
    
    # 降噪
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_5_denoised.jpg"), binary)
    
    # 检测横线和竖线 - 使用更灵活的参数
    min_line_length_h = max(20, w // 20)  # 水平线最小长度
    min_line_length_v = max(20, h // 20)  # 垂直线最小长度
    
    # 检测横线
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (min_line_length_h, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=3)
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_6_horizontal_lines.jpg"), horizontal_lines)
    
    # 检测竖线
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, min_line_length_v))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_7_vertical_lines.jpg"), vertical_lines)
    
    # 检测表格结构的另一种方法：霍夫变换
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_8_edges.jpg"), edges)
    
    # 检测直线
    h_lines = cv2.HoughLinesP(horizontal_lines, 1, np.pi/180, 50, minLineLength=w//3, maxLineGap=20)
    v_lines = cv2.HoughLinesP(vertical_lines, 1, np.pi/180, 50, minLineLength=h//3, maxLineGap=20)
    
    # 创建可视化图像
    if debug:
        vis_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # 绘制检测到的线
        if h_lines is not None:
            for line in h_lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(vis_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        if v_lines is not None:
            for line in v_lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(vis_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_9_detected_lines.jpg"), vis_img)
    
    # 提取行和列的位置
    rows = [0]  # 起始位置
    if h_lines is not None:
        for line in h_lines:
            rows.append(line[0][1])  # y坐标
    rows.append(h)  # 结束位置
    
    cols = [0]  # 起始位置
    if v_lines is not None:
        for line in v_lines:
            cols.append(line[0][0])  # x坐标
    cols.append(w)  # 结束位置
    
    # 排序并去重
    rows = sorted(set(rows))
    cols = sorted(set(cols))
    
    # 确保至少有3列（根据图片示例）
    if len(cols) < 4:  # 需要至少3列+边界
        # 如果检测不到足够的列，强制分为3列
        cols = [0, w//3, 2*w//3, w]
    
    # 过滤过近的行和列（合并相邻的行/列）
    def filter_close_points(points, min_dist=10):
        if len(points) <= 1:
            return points
        
        filtered = [points[0]]
        for i in range(1, len(points)):
            if points[i] - filtered[-1] >= min_dist:
                filtered.append(points[i])
        
        return filtered
    
    # 过滤相近的行和列
    rows = filter_close_points(rows)
    cols = filter_close_points(cols)
    
    return rows, cols, gray

def ocr_with_timeout(image, config='--psm 7 --oem 3 -l chi_sim+eng'):
    """带超时的OCR识别"""
    result = [""]  # 使用列表存储结果，便于在线程中修改
    
    def ocr_task():
        try:
            result[0] = pytesseract.image_to_string(image, config=config).strip()
        except Exception as e:
            print(f"OCR错误: {e}")
    
    # 创建并启动线程
    thread = threading.Thread(target=ocr_task)
    thread.daemon = True
    thread.start()
    
    # 等待线程完成，或超时
    thread.join(OCR_TIMEOUT)
    
    # 如果线程仍在运行，返回空字符串
    if thread.is_alive():
        print("OCR超时")
        return ""
    
    return result[0]

def process_cell(cell_data):
    """处理单个单元格，用于并行处理"""
    i, j, cell, is_number_col = cell_data
    
    # 添加边框以避免文字被裁剪
    cell = cv2.copyMakeBorder(cell, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
    
    # 增强单元格图像
    cell_enhanced = enhance_image(cell)
    
    # 二值化以增强文字
    _, cell_bin = cv2.threshold(cell_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 进一步处理：去除噪点
    kernel = np.ones((2, 2), np.uint8)
    cell_bin = cv2.morphologyEx(cell_bin, cv2.MORPH_OPEN, kernel)
    
    # 根据列类型选择合适的OCR配置
    if is_number_col:
        # 数字列
        text = ocr_with_timeout(cell_bin, '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')
    else:
        # 尝试不同的PSM模式
        configs = [
            '--psm 7 --oem 3 -l chi_sim+eng',
            '--psm 6 --oem 3 -l chi_sim+eng',
            '--psm 8 --oem 3 -l chi_sim+eng'
        ]
        
        text = ""
        for config in configs:
            text = ocr_with_timeout(cell_bin, config)
            if text:
                break
    
    # 后处理：清理文本
    text = text.replace('\n', ' ').replace('\r', '')
    
    return i, j, text, cell_bin

def extract_table_from_image(image_path, debug=True):
    print(f"处理图片: {os.path.basename(image_path)}")
    start_time = time.time()
    
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图片: {image_path}")
        return []
    
    # 保存原始图片副本用于调试
    debug_base = os.path.splitext(os.path.basename(image_path))[0]
    if debug:
        cv2.imwrite(os.path.join(DEBUG_DIR, f"{debug_base}_1_original.jpg"), img)
    
    # 检测表格结构
    rows, cols, gray = detect_table_structure(img, debug_base, debug)
    
    # 确保行列至少有2个点
    if len(rows) < 2 or len(cols) < 2:
        print(f"行或列数量不足: 行={len(rows)}, 列={len(cols)}")
        # 创建一个均匀的网格
        h, w = img.shape[:2]
        rows = [0, h//3, 2*h//3, h]
        cols = [0, w//3, 2*w//3, w]
    
    print(f"检测到 {len(rows)-1} 行, {len(cols)-1} 列")
    
    # 如果行或列太多，可能是误检测，限制最大数量
    max_rows = 30
    max_cols = 10
    if len(rows) > max_rows:
        print(f"检测到的行数过多 ({len(rows)-1})，限制为 {max_rows-1}")
        # 均匀选择行
        step = len(rows) // max_rows
        rows = rows[::step]
        if len(rows) > max_rows:
            rows = rows[:max_rows]
        if rows[-1] != img.shape[0]:
            rows.append(img.shape[0])
    
    if len(cols) > max_cols:
        print(f"检测到的列数过多 ({len(cols)-1})，限制为 {max_cols-1}")
        # 均匀选择列
        step = len(cols) // max_cols
        cols = cols[::step]
        if len(cols) > max_cols:
            cols = cols[:max_cols]
        if cols[-1] != img.shape[1]:
            cols.append(img.shape[1])
    
    # 提取每个单元格内容
    h, w = img.shape[:2]
    
    # 准备单元格数据
    cells_to_process = []
    for i in range(len(rows) - 1):
        for j in range(len(cols) - 1):
            # 确保坐标有效
            y1, y2 = max(0, rows[i]), min(h, rows[i+1])
            x1, x2 = max(0, cols[j]), min(w, cols[j+1])
            
            if y2 <= y1 or x2 <= x1:
                continue
                
            # 提取单元格图像
            cell = gray[y1:y2, x1:x2]
            
            # 判断是否为数字列（第三列）
            is_number_col = (j == 2)
            
            cells_to_process.append((i, j, cell, is_number_col))
    
    # 创建结果矩阵
    table_data = [["" for _ in range(len(cols)-1)] for _ in range(len(rows)-1)]
    
    # 并行处理单元格
    print(f"开始处理 {len(cells_to_process)} 个单元格...")
    
    # 使用线程池并行处理单元格
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交所有任务
        future_to_cell = {executor.submit(process_cell, cell_data): cell_data for cell_data in cells_to_process}
        
        # 处理结果
        for i, future in enumerate(concurrent.futures.as_completed(future_to_cell)):
            cell_data = future_to_cell[future]
            try:
                row_idx, col_idx, text, cell_bin = future.result()
                table_data[row_idx][col_idx] = text
                
                # 保存单元格图像用于调试
                if debug:
                    cell_dir = os.path.join(DEBUG_DIR, f"{debug_base}_cells")
                    os.makedirs(cell_dir, exist_ok=True)
                    cv2.imwrite(os.path.join(cell_dir, f"cell_{row_idx}_{col_idx}.jpg"), cell_bin)
                
                # 显示进度
                if (i+1) % 10 == 0 or (i+1) == len(cells_to_process):
                    print(f"已处理 {i+1}/{len(cells_to_process)} 个单元格 ({(i+1)/len(cells_to_process)*100:.1f}%)")
            except Exception as e:
                print(f"处理单元格 {cell_data[0]}_{cell_data[1]} 时出错: {e}")
    
    # 过滤空行
    table_data = [row for row in table_data if any(cell.strip() for cell in row)]
    
    print(f"表格提取完成，用时 {time.time() - start_time:.1f} 秒")
    return table_data

def process_all_images():
    """遍历处理所有图片"""
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"已创建输入文件夹: {INPUT_DIR}")
        print(f"请将图片放入 {INPUT_DIR} 文件夹后重新运行程序")
        return
        
    image_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(SUPPORTED_FORMATS)]
    
    if not image_files:
        print(f"在 {INPUT_DIR} 中未找到支持的图片文件")
        print(f"支持的格式: {', '.join(SUPPORTED_FORMATS)}")
        return
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    for filename in image_files:
        image_path = os.path.join(INPUT_DIR, filename)
        print(f"\n开始处理: {filename}")
        
        try:
            table_data = extract_table_from_image(image_path)
            
            if table_data:
                # 检查数据是否有效
                valid_rows = [row for row in table_data if any(cell.strip() for cell in row)]
                if valid_rows:
                    # 确保所有行的列数一致
                    max_cols = max(len(row) for row in valid_rows)
                    padded_data = [row + [''] * (max_cols - len(row)) for row in valid_rows]
                    df = pd.DataFrame(padded_data)
                    print(f"成功提取表格，行数: {len(df)}, 列数: {len(df.columns)}")
                else:
                    df = pd.DataFrame([['未检测到有效表格内容']])
                    print("未检测到有效表格内容")
            else:
                df = pd.DataFrame([['未检测到表格']])
                print("未检测到表格")
            
            # 时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_name = os.path.splitext(filename)[0] + f"_{timestamp}.xlsx"
            output_path = os.path.join(OUTPUT_DIR, excel_name)
            df.to_excel(output_path, index=False, header=False)
            print(f"已保存Excel文件: {excel_name}")
        except Exception as e:
            print(f"处理图片 {filename} 时出错: {e}")
            # 保存错误信息到Excel
            df = pd.DataFrame([[f"处理错误: {str(e)}"]])
            excel_name = os.path.splitext(filename)[0] + '_error.xlsx'
            output_path = os.path.join(OUTPUT_DIR, excel_name)
            df.to_excel(output_path, index=False, header=False)

if __name__ == '__main__':
    print("图片表格识别程序启动")
    print(f"输入文件夹: {INPUT_DIR}")
    print(f"输出文件夹: {OUTPUT_DIR}")
    print(f"调试图像文件夹: {DEBUG_DIR}")
    process_all_images()
    print('\n全部图片处理完成。')
