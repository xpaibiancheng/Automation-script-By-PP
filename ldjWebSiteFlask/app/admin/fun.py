import os
from ..config import HostBaseUrl
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from bs4 import BeautifulSoup


# 判断是否是图片类型文件
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']

# 保存图片文件的到后端并返回完整的URL地址
def uplode_image_fun(file,beFlag):
    if file and allowed_file(file.filename):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = secure_filename(f"{beFlag}{timestamp}.{file.filename.rsplit('.', 1)[1]}")
        file_path = os.path.join(current_app.root_path, 'static/images', filename)
        file.save(file_path)
        entirePath = f'{HostBaseUrl}/static/images/{filename}'
        return entirePath
    else:
        return None

# 去除有关所有网页元素 并可以索引保留前多少的文字
def extract_text(html_content, max_length=100):
    """

    从HTML内容中提取纯文本，并限制返回的文本长度。
    :param html_content: 包含HTML标签的字符串
    :param max_length: 返回文本的最大长度，默认为100
    :return: 去除HTML标签后的前max_length个字符的文本

    """
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 获取所有文本
    text = soup.get_text()

    # 去除多余的空白字符
    cleaned_text = ' '.join(text.split())

    # 只保留前max_length个字符
    truncated_text = cleaned_text[:max_length]

    return truncated_text
import datetime
def ms_str_translate(item,flag):
    if flag == "ms":
        # 如果 item['update_time'] 是以毫秒为单位的时间戳
        update_time_timestamp_ms = item
        update_time_temp = datetime.datetime.fromtimestamp(update_time_timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
        return update_time_temp
    else:
        # 假设 item['update_time'] 是 Unix 时间戳
        update_time_timestamp = item
        update_time_temp = datetime.datetime.fromtimestamp(update_time_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        return update_time_temp

