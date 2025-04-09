import requests
from docx import Document
#注意事项：

#仅适用于有官方字幕（CC字幕）的视频

#如果视频有多个字幕（如中英双语），默认下载第一个

#需要网络连接正常，且视频未设置访问限制



def get_cid(bv_id):
    """获取视频的CID"""
    url = f"https://api.bilibili.com/x/player/pagelist?bvid={bv_id}&jsonp=jsonp"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.json()['data'][0]['cid']


def get_subtitle_info(bv_id, cid):
    """获取字幕信息"""
    url = f"https://api.bilibili.com/x/player/v2?bvid={bv_id}&cid={cid}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.json()['data']['subtitle']['subtitles']


def download_subtitle(subtitle_url):
    """下载字幕内容"""
    response = requests.get(f"https:{subtitle_url}", headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return [item['content'] for item in response.json()['body']]


def save_to_docx(text_list, filename):
    """保存到Word文档"""
    doc = Document()
    for text in text_list:
        doc.add_paragraph(text)
    doc.save(filename)
    print(f"字幕已保存到 {filename}")


def main():
    bv_id = input("请输入B站视频BV号（例如：BV1xx411x7xx）: ").strip()

    try:
        # 获取视频基本信息
        cid = get_cid(bv_id)

        # 获取字幕信息
        subtitles = get_subtitle_info(bv_id, cid)
        if not subtitles:
            print("该视频没有字幕")
            return

        # 选择第一个字幕（通常为中文）
        subtitle_url = subtitles[0]['subtitle_url']
        print(f"检测到{len(subtitles)}个字幕，正在下载第一个字幕...")

        # 下载并保存字幕
        subtitle_text = download_subtitle(subtitle_url)
        save_to_docx(subtitle_text, "b站字幕.docx")

    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()