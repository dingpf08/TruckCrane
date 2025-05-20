import os
import re
import tkinter as tk
from tkinter import filedialog
import shutil
'''该脚本用于批量处理一个文件夹下的所有 PDF 文件，实现两个主要功能：
提取 PDF 文件名中的"型号"信息，并将所有型号按顺序写入同一文件夹下的 extracted_models.txt 文件，每行一个型号。
为每个 PDF 文件自动加上编号前缀，编号顺序与型号提取顺序一致。重命名后的文件格式为：
1-原文件名.pdf
2-原文件名.pdf
   ...
'''

'''提取规则
对于每个 PDF 文件，脚本会按如下规则从文件名中提取"型号"：
优先规则：括号结尾提取
匹配文件名中以右括号（英文 ) 或中文 ））结尾的部分，包括括号本身。
例如：
ABC-123(20T).pdf → 提取 ABC-123(20T)
XYZ-456）.pdf → 提取 XYZ-456）
正则表达式：^(.*?[\)\）])
含义：从开头开始，尽可能少地匹配任意字符，直到遇到第一个右括号（英文或中文）。
次级规则：字母数字连字符前缀
如果不符合上面的括号规则，则匹配文件名开头连续的字母、数字或连字符。
例如：
DEF-789说明书.pdf → 提取 DEF-789
GHI123-附录.pdf → 提取 GHI123-
正则表达式：^([A-Za-z0-9\-]+)
含义：从开头开始，匹配一个或多个字母、数字或连字符。
兜底规则：文件名本身
如果上述两条规则都不匹配，则直接使用去掉扩展名的文件名作为型号。
'''

'''
使用方法：
运行脚本：
弹出窗口，选择包含 PDF 文件的目标文件夹。
程序自动处理，生成 extracted_models.txt 并为 PDF 文件加编号前缀。
查看结果：
extracted_models.txt 文件中每行是一个提取到的型号。
文件夹下的 PDF 文件已自动加上编号前缀。
'''
def extract_model_names_from_folder():
    """
    批量提取PDF文件型号，并为每个PDF文件加上编号前缀。
    """
    # Use tkinter to select a directory
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="选择包含PDF文件的文件夹")

    if not folder_path:
        print("未选择任何文件夹，程序退出。")
        return

    # Prepare regex patterns
    pattern_bracket = re.compile(r'^(.*?[\)\）])')
    pattern_simple = re.compile(r'^([A-Za-z0-9\-]+)')

    # 英文型号后缀列表
    EN_SUFFIXES = [
        'Pro', 'Plus', 'Max', 'Classic', 'Hybrid', 'PlugIn'
    ]
    # 构造正则，匹配如 Pro、Plus、Max 等后面跟任意内容的情况
    suffix_pattern = re.compile(rf"({'|'.join(EN_SUFFIXES)})(?=[^A-Za-z]|$).*$", re.IGNORECASE)

    # 优化型号提取规则
    # 1. 优先匹配"型号主体+括号内容"，如 STC250C5-8(25款)
    # 2. 没有括号时，遇到第一个汉字或特殊字符就截断
    # 3. 英文后缀依然保留
    pattern_full = re.compile(r'^([A-Za-z0-9\-]+(?:[\(（][^\)）]+[\)）])?)')

    extracted = []
    pdf_files = []  # 记录原始PDF文件名
    for entry in os.listdir(folder_path):
        if entry.lower().endswith('.pdf') and os.path.isfile(os.path.join(folder_path, entry)):
            base_name = os.path.splitext(entry)[0]
            # 优先匹配"型号主体+括号内容"
            m = pattern_full.match(base_name)
            if m:
                model = m.group(1)
            else:
                # 没有括号时，遇到第一个汉字或特殊字符就截断
                model = re.split(r'[\u4e00-\u9fa5，。、《》""''！￥……（）—【】·~!@#￥%……&*（）\-+=|\\{}\[\]:;"\'<>,.?/]', base_name)[0]
            # 进一步处理：如有Pro、Plus等后缀，去掉其后的内容
            model = suffix_pattern.sub(r"\1", model)
            extracted.append(model)
            pdf_files.append(entry)

    # Write to extracted_models.txt in the same folder
    output_file = os.path.join(folder_path, 'extracted_models.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, (model, pdf_file) in enumerate(zip(extracted, pdf_files), 1):
            line = f"{idx} {model}"
            f.write(line + '\n')
            # 创建同名文件夹
            folder_name = os.path.join(folder_path, line)
            os.makedirs(folder_name, exist_ok=True)
            # 复制PDF文件到该文件夹
            src_pdf = os.path.join(folder_path, pdf_file)
            dst_pdf = os.path.join(folder_name, pdf_file)
            shutil.copy2(src_pdf, dst_pdf)

    # 先去除所有PDF文件名前的编号-前缀（如1-、23-等）
    pattern_prefix = re.compile(r'^\d+-')
    for entry in os.listdir(folder_path):
        if entry.lower().endswith('.pdf') and os.path.isfile(os.path.join(folder_path, entry)):
            if pattern_prefix.match(entry):
                new_name = pattern_prefix.sub('', entry)
                old_path = os.path.join(folder_path, entry)
                new_path = os.path.join(folder_path, new_name)
                # 避免覆盖
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                else:
                    print(f"跳过去前缀，目标文件已存在: {new_name}")

    # 按顺序为PDF文件重命名，加编号前缀，并记录新文件名
    renamed_files = []
    for idx, old_name in enumerate(pdf_files, 1):
        old_path = os.path.join(folder_path, old_name)
        new_name = f"{idx}-{old_name}"
        new_path = os.path.join(folder_path, new_name)
        # 避免重名覆盖
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            renamed_files.append(new_name)
        else:
            print(f"跳过重命名，目标文件已存在: {new_name}")
            renamed_files.append(new_name)  # 仍然加入列表，保证顺序一致

    print(f"已提取 {len(extracted)} 个型号，结果保存在:\n{output_file}")
    print("PDF文件已按顺序编号重命名。")

    # 复制重命名后的PDF文件到对应文件夹
    for idx, (model, pdf_file) in enumerate(zip(extracted, renamed_files), 1):
        line = f"{idx} {model}"
        folder_name = os.path.join(folder_path, line)
        os.makedirs(folder_name, exist_ok=True)
        src_pdf = os.path.join(folder_path, pdf_file)
        dst_pdf = os.path.join(folder_name, pdf_file)
        shutil.copy2(src_pdf, dst_pdf)


if __name__ == "__main__":
    extract_model_names_from_folder()

