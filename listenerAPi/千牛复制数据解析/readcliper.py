# 使用此指令前，请确保安装必要的Python库，例如使用以下命令安装：
# pip install pyperclip pillow pywin32

import pyperclip
from PIL import ImageGrab, Image
import io
import os

# text = pyperclip.paste()   使用pyperclip 的 paste返回读取剪贴板的数据
# ImageGrab.grabclipboard()  PIL 的imageGrab 的grapbclipboard()方法 可以获取剪贴板中的图片数据


def read_clipboard_content(save_folder):
    """
    title: 读取剪贴板图文内容
    description: 读取剪贴板中的所有内容，包括文本和图像，将图像保存到指定文件夹 % save_folder % 中。
    inputs:
        - save_folder (folder): 图像保存文件夹路径，eg: "C:/clipboard_images"
    outputs:
        - result (dict): 包含文本和图像信息的字典，eg: "{'text': '剪贴板文本', 'images': ['image1.png']}"
    """
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    def _read_clipboard_text():
        """读取剪贴板文本内容"""
        try:
            text = pyperclip.paste()
            return text if text else ""
        except Exception as e:
            return f"读取文本失败: {str(e)}"
    
    def _read_clipboard_image():
        """读取剪贴板图像内容并保存"""
        try:
            image = ImageGrab.grabclipboard()
            if image:
                # 生成唯一文件名
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"clipboard_image_{timestamp}.png"
                filepath = os.path.join(save_folder, filename)
                
                # 保存图像
                image.save(filepath, 'PNG')
                return filename
            return None
        except Exception as e:
            return f"读取图像失败: {str(e)}"
    
    # 读取剪贴板内容
    text_content = _read_clipboard_text()
    image_filename = _read_clipboard_image()
    
    result = {
        'text': text_content,
        'images': [image_filename] if image_filename and not image_filename.startswith("读取图像失败") else [],
        'save_folder': save_folder
    }
    
    if not text_content and not result['images']:
        raise ValueError("剪贴板中没有检测到文本或图像内容")
    
    return result


def parse_qianniu_chat_to_json(text_content):
    """
    将千牛聊天记录解析为JSON格式
    支持多种格式，包括用户名直接连接时间的情况
    """
    if not text_content:
        return []
    
    # 分割消息块
    messages = []
    lines = text_content.split('\r\n')
    
    def _is_valid_time_format(time_str):
        """检查是否是有效的时间格式"""
        try:
            parts = time_str.split()
            if len(parts) == 2:
                date_part = parts[0]
                time_part = parts[1]
                date_parts = date_part.split('-')
                if len(date_parts) == 3:
                    year, month, day = date_parts
                    if (year.isdigit() and month.isdigit() and day.isdigit() and
                        2020 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                        time_parts = time_part.split(':')
                        if len(time_parts) == 3:
                            hour, minute, second = time_parts
                            if (hour.isdigit() and minute.isdigit() and second.isdigit() and
                                0 <= int(hour) <= 23 and 0 <= int(minute) <= 59 and 0 <= int(second) <= 59):
                                return True
        except:
            pass
        return False

    def _extract_username_timestamp(line):
        """从行中提取用户名和时间戳，支持无空格连接"""
        import re
        # 匹配时间戳模式：YYYY-M-D H:MM:SS
        time_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}:\d{2})$', line)
        if time_match:
            timestamp = time_match.group(1)
            username = line[:time_match.start()].strip()
            if _is_valid_time_format(timestamp):
                return username, timestamp
        return None, None

    def _is_new_message_start(line, current_index, all_lines):
        """检查是否是新消息的开始"""
        line = line.strip()
        if not line:
            return False
        
        # 检查撤回消息
        if line.endswith('撤回了一条消息'):
            return True
        
        # 检查无空格连接的用户名+时间
        username, timestamp = _extract_username_timestamp(line)
        if username and timestamp:
            return True
        
        # 原有检查
        parts = line.split()
        if len(parts) >= 3 and _is_valid_time_format(' '.join(parts[-2:])):
            return True
        
        if ' --> ' in line and len(parts) >= 4 and _is_valid_time_format(' '.join(parts[-2:])):
            return True
        
        if (current_index + 1 < len(all_lines) and 
            all_lines[current_index + 1].strip().startswith('20')):
            return True
        
        return False
    
    def _is_skip_line(line):
        """检查是否需要跳过该行"""
        skip_keywords = [
            '当前用户来自', '商品详情页', '商品推荐', '这些非常适合您的商品可以一起看看～～', 
            '由 服务助手 转交给', '原因：【离线留言自动分配】', '千牛'
        ]
        
        if not line:
            return True
        
        if line.startswith('http') or line.startswith('`http'):
            return True
            
        if line.startswith('¥') or line == '¥':
            return True
            
        if line.startswith('电影'):
            return True
            
        for keyword in skip_keywords:
            if line == keyword:
                return True
                
        return False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # 检查撤回消息
        if '撤回了一条消息' in line:
            parts = line.split(' 撤回了一条消息')
            if len(parts) == 2 and parts[1] == '':
                messages.append({
                    'username': parts[0].strip(),
                    'timestamp': None,
                    'message': '撤回了一条消息',
                    'status': None
                })
                i += 1
                continue
        
        # 尝试提取用户名和时间
        username, timestamp = _extract_username_timestamp(line)
        new_format_match = bool(username and timestamp)
        
        if not new_format_match:
            # 检查特殊格式
            if ' --> ' in line:
                try:
                    user_part, rest = line.split(' --> ', 1)
                    receiver, time_part = rest.rsplit(' ', 1)
                    if _is_valid_time_format(time_part):
                        username = user_part + ' --> ' + receiver
                        timestamp = time_part
                        new_format_match = True
                except:
                    pass
        
        # 如果匹配成功，或者旧格式
        if new_format_match or (i + 1 < len(lines) and lines[i + 1].strip().startswith('20')):
            if not new_format_match:
                username = line
                timestamp = lines[i + 1].strip()
                i += 2
            else:
                i += 1
            
            message_content = []
            status_flags = []
            url_content = []
            
            while i < len(lines):
                content_line = lines[i].strip()
                
                if _is_new_message_start(content_line, i, lines):
                    break
                
                # 收集URL
                if content_line.startswith('http') or content_line.startswith('`http'):
                    # 提取URL
                    url = content_line.strip('`')
                    url_content.append(url)
                    i += 1
                    continue
                
                # 跳过系统消息和特殊内容
                if _is_skip_line(content_line):
                    i += 1
                    continue
                
                if content_line in ['已读', '未读', '发送中']:
                    status_flags.append(content_line)
                    i += 1
                    continue
                
                if content_line:
                    message_content.append(content_line)
                
                i += 1
            
            message_str = '\n'.join(message_content).strip()
            if message_str or status_flags or url_content:
                message_data = {
                    'username': username,
                    'timestamp': timestamp,
                    'message': message_str,
                    'status': status_flags[-1] if status_flags else None
                }
                
                # 添加URL信息
                if url_content:
                    message_data['urls'] = url_content
                
                messages.append(message_data)
        else:
            i += 1
    
    return messages


if __name__ == "__main__":
    save_folder = "千牛复制数据解析"
    result = read_clipboard_content(save_folder)
    
    # 解析聊天记录为JSON
    chat_json = parse_qianniu_chat_to_json(result['text'])
    
    import json
    print("原始剪贴板内容:")
    print(result)
    print("\n解析后的JSON格式:")
    print(json.dumps(chat_json, ensure_ascii=False, indent=2))
