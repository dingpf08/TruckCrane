import lxml.html
import requests
from lxml import etree
import os
import re
#从公众号将文章中的图片爬取下来
def sanitize_filename(filename):
    """Sanitize the filename by removing or replacing invalid characters and limiting length."""
    filename = re.sub(r'\?.*', '', filename)  # Remove query parameters
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)  # Remove invalid path characters
    return filename

def get_image_format(url):
    """Extracts the image format from the URL, defaulting to jpg if unclear."""
    possible_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    fmt = url.split('.')[-1].split('?')[0]
    if fmt not in possible_formats:
        fmt = 'jpg'  # Default to jpg if the format is not one of the recognized types
    return fmt

def main():
    test_url = 'https://mp.weixin.qq.com/s/wO0fm0pzCExEoEFwX3cmkA'
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58'
    }
    resp = requests.get(url=test_url, headers=headers).text
    html1 = etree.HTML(resp)

    title = html1.xpath("//*[@id='activity-name']/text()")
    if title:
        print(title[0].strip())

    pic_save_dir = os.path.join(os.getcwd(), '7-【期末复习】人教版初二八年级下册生物期末考试知识点总结/')
    os.makedirs(pic_save_dir, exist_ok=True)

    img_list = html1.xpath("//img/@data-src")
    for i, img in enumerate(img_list):
        img_filename = img.split('/')[-1]  # Get the last part of the URL
        base_name = sanitize_filename(img_filename.split('.')[0])
        fmt = get_image_format(img)  # Get or default the image format

        # Use index to create a unique filename
        filename = os.path.join(pic_save_dir, f"{base_name}_{i}.{fmt}")
        img_resp = requests.get(img).content
        with open(filename, "wb+") as f:
            f.write(img_resp)
            print(f"Downloaded {filename}")

if __name__ == '__main__':
    main()
