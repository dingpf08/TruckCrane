import cv2
import numpy as np

def adjust_colors(img, alpha=1.0, beta=-10):
    """调整图像亮度和对比度，降低亮度和对比度增强的程度"""
    new_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return new_img

def restore_watermarked_image(image_path, output_path):
    # 加载图像
    img = cv2.imread(image_path)
    if img is None:
        print("Error loading image")
        return

    # 转换为灰度图像并创建掩码
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    # 使用掩码修复图像区域
    repaired = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

    # 调整色彩平衡与对比度
    restored_img = adjust_colors(repaired, alpha=1.0, beta=-10)  # 减小alpha和beta值以减轻对比度和亮度的增强

    # 保存结果
    cv2.imwrite(output_path, restored_img)
    print(f"Restored image saved to {output_path}")

if __name__ == "__main__":
    image_path = r'C:\Users\CN\Desktop\Waste\640_1.jpg'
    output_path = r'C:\Users\CN\Desktop\Waste\640_1_removewatermark.jpg'
    restore_watermarked_image(image_path, output_path)
