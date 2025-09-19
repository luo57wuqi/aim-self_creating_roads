# 使用此指令前，请确保安装必要的Python库，例如使用以下命令安装：
# pip install pyperclip pillow pywin32

# =============================================================================
# 文件功能说明：
# =============================================================================
# 本文件包含两个主要功能模块：
# 1. read_clipboard_content() - 读取剪贴板中的文本和图像内容
#    - 支持读取剪贴板文本内容
#    - 支持读取剪贴板图像并保存到指定文件夹
#    - 返回包含文本和图像信息的字典
#
# 2. parse_qianniu_chat_to_json() - 将千牛聊天记录解析为JSON格式
#    - 支持多种千牛聊天记录格式解析
#    - 处理用户名与时间戳的各种连接方式（有空格/无空格）
#    - 支持撤回消息识别和处理
#    - 支持消息状态标识提取（已读/未读/发送中）
#    - 支持URL链接提取和单独存储
#    - 过滤系统消息和广告内容
#    - 返回结构化的JSON格式消息列表
#
# 使用示例：
# - 直接运行脚本：python readcliper.py
# - 导入使用：from readcliper import read_clipboard_content, parse_qianniu_chat_to_json
# =============================================================================

import pyperclip  # 剪贴板操作库
from PIL import ImageGrab, Image  # 图像处理库，用于读取剪贴板图像
import io  # 输入输出流处理
import os  # 操作系统接口，用于文件和目录操作




def read_clipboard_content(save_folder):
    """
    title: 读取剪贴板图文内容
    description: 读取剪贴板中的所有内容，包括文本和图像，将图像保存到指定文件夹 % save_folder % 中。
    inputs:
        - save_folder (folder): 图像保存文件夹路径，eg: "C:/clipboard_images"
    outputs:
        - result (dict): 包含文本和图像信息的字典，eg: "{'text': '剪贴板文本', 'images': ['image1.png']}"
    """
    
    # 检查保存文件夹是否存在，如果不存在则创建
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    def _read_clipboard_text():
        """读取剪贴板文本内容"""
        try:
            text = pyperclip.paste()  # 使用pyperclip读取剪贴板文本
            return text if text else ""  # 如果文本为空则返回空字符串
        except Exception as e:
            return f"读取文本失败: {str(e)}"  # 异常处理，返回错误信息
    
    def _read_clipboard_image():
        """读取剪贴板图像内容并保存"""
        try:
            image = ImageGrab.grabclipboard()  # 从剪贴板获取图像
            if image:
                # 生成唯一文件名 - 使用当前时间戳
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"clipboard_image_{timestamp}.png"  # 创建带时间戳的文件名
                filepath = os.path.join(save_folder, filename)  # 拼接完整文件路径
                
                # 保存图像到指定路径
                image.save(filepath, 'PNG')
                return filename  # 返回保存的文件名
            return None  # 剪贴板中没有图像时返回None
        except Exception as e:
            return f"读取图像失败: {str(e)}"  # 异常处理，返回错误信息
    
    # 读取剪贴板内容 - 分别读取文本和图像
    text_content = _read_clipboard_text()
    image_filename = _read_clipboard_image()
    
    # 构建结果字典
    result = {
        'text': text_content,  # 剪贴板文本内容
        'images': [image_filename] if image_filename and not image_filename.startswith("读取图像失败") else [],  # 图像文件名列表（过滤错误信息）
        'save_folder': save_folder  # 保存文件夹路径
    }
    
    # 检查是否读取到任何内容，如果没有则抛出异常
    if not text_content and not result['images']:
        raise ValueError("剪贴板中没有检测到文本或图像内容")
    
    return result


def parse_qianniu_chat_to_json(text_content):
    """
    将千牛聊天记录解析为JSON格式
    支持多种格式，包括用户名直接连接时间的情况
    """
    # 如果输入内容为空，直接返回空列表
    if not text_content:
        return []
    
    # 分割消息块 - 按Windows换行符分割
    messages = []  # 存储解析后的消息列表
    lines = text_content.split('\r\n')  # 按Windows换行符分割文本
    
    def _is_valid_time_format(time_str):
        """检查是否是有效的时间格式"""
        try:
            parts = time_str.split()  # 按空格分割时间字符串
            if len(parts) == 2:  # 确保有日期和时间两部分
                date_part = parts[0]  # 日期部分
                time_part = parts[1]  # 时间部分
                date_parts = date_part.split('-')  # 按-分割日期
                if len(date_parts) == 3:  # 确保有年月日三部分
                    year, month, day = date_parts  # 分别获取年月日
                    # 检查日期格式的有效性：年份在2020-2030，月份1-12，日期1-31
                    if (year.isdigit() and month.isdigit() and day.isdigit() and
                        2020 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                        time_parts = time_part.split(':')  # 按:分割时间
                        if len(time_parts) == 3:  # 确保有时分秒三部分
                            hour, minute, second = time_parts  # 分别获取时分秒
                            # 检查时间格式的有效性：小时0-23，分钟0-59，秒0-59
                            if (hour.isdigit() and minute.isdigit() and second.isdigit() and
                                0 <= int(hour) <= 23 and 0 <= int(minute) <= 59 and 0 <= int(second) <= 59):
                                return True  # 格式有效
        except:
            pass  # 任何异常都返回False
        return False  # 格式无效

    def _extract_username_timestamp(line):
        """从行中提取用户名和时间戳，支持无空格连接"""
        import re  # 导入正则表达式模块
        # 匹配时间戳模式：YYYY-M-D H:MM:SS（在行末尾）
        time_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}:\d{2})$', line)
        if time_match:  # 如果找到匹配的时间戳
            timestamp = time_match.group(1)  # 获取时间戳字符串
            username = line[:time_match.start()].strip()  # 获取时间戳之前的部分作为用户名
            if _is_valid_time_format(timestamp):  # 验证时间戳格式是否有效
                return username, timestamp  # 返回用户名和时间戳
        return None, None  # 未找到有效的时间戳格式

    def _is_new_message_start(line, current_index, all_lines):
        """检查是否是新消息的开始"""
        line = line.strip()  # 去除行首尾空白字符
        if not line:  # 如果行为空
            return False  # 不是新消息开始
        
        # 检查撤回消息 - 以"撤回了一条消息"结尾的行
        if line.endswith('撤回了一条消息'):
            return True  # 是撤回消息，视为新消息开始
        
        # 检查无空格连接的用户名+时间格式
        username, timestamp = _extract_username_timestamp(line)
        if username and timestamp:  # 如果成功提取到用户名和时间戳
            return True  # 是新消息开始
        
        # 原有检查 - 检查标准格式（用户名 时间戳）
        parts = line.split()  # 按空格分割行
        if len(parts) >= 3 and _is_valid_time_format(' '.join(parts[-2:])):  # 最后两部分是时间戳
            return True  # 是新消息开始
        
        # 检查特殊格式（用户 --> 接收者 时间戳）
        if ' --> ' in line and len(parts) >= 4 and _is_valid_time_format(' '.join(parts[-2:])):
            return True  # 是特殊格式的新消息
        
        # 检查下一行是否以20开头（可能是时间戳）
        if (current_index + 1 < len(all_lines) and 
            all_lines[current_index + 1].strip().startswith('20')):  # 下一行可能是时间戳
            return True  # 可能是新消息开始
        
        return False  # 不是新消息开始
    
    def _is_skip_line(line):
        """检查是否需要跳过该行"""
        # 定义需要跳过的关键词列表 - 这些都是系统消息或广告内容
        skip_keywords = [
            '当前用户来自', '商品详情页', '商品推荐', '这些非常适合您的商品可以一起看看～～', 
            '由 服务助手 转交给', '原因：【离线留言自动分配】', '千牛'
        ]
        
        if not line:  # 如果行为空
            return True  # 跳过空行
        
        # 跳过URL链接（这些会在专门的URL处理中收集）
        if line.startswith('http') or line.startswith('`http'):
            return True  # 跳过URL行
            
        # 跳过价格标识
        if line.startswith('¥') or line == '¥':
            return True  # 跳过价格符号
            
        # 跳过电影相关提示
        if line.startswith('电影'):
            return True  # 跳过电影提示
            
        # 检查是否匹配跳过关键词
        for keyword in skip_keywords:
            if line == keyword:  # 完全匹配关键词
                return True  # 跳过系统消息
                
        return False  # 不跳过该行
    
    # 主循环 - 逐行处理聊天记录
    i = 0  # 行索引初始化
    while i < len(lines):  # 遍历所有行
        line = lines[i].strip()  # 获取当前行并去除首尾空白
        if not line:  # 如果行为空
            i += 1  # 跳过空行
            continue
            
        # 检查撤回消息 - 格式：用户名 撤回了一条消息
        if '撤回了一条消息' in line:
            parts = line.split(' 撤回了一条消息')  # 按撤回消息分割
            if len(parts) == 2 and parts[1] == '':  # 确保格式正确
                messages.append({  # 添加撤回消息记录
                    'username': parts[0].strip(),  # 用户名
                    'timestamp': None,  # 撤回消息没有时间戳
                    'message': '撤回了一条消息',  # 消息内容
                    'status': None  # 撤回消息没有状态
                })
                i += 1  # 处理下一行
                continue  # 跳过本次循环的剩余部分
        
        # 尝试提取用户名和时间 - 支持无空格连接格式
        username, timestamp = _extract_username_timestamp(line)
        new_format_match = bool(username and timestamp)  # 是否匹配新格式
        
        if not new_format_match:  # 如果不是新格式
            # 检查特殊格式 - 用户 --> 接收者 时间戳
            if ' --> ' in line:
                try:
                    user_part, rest = line.split(' --> ', 1)  # 分割用户和接收者部分
                    receiver, time_part = rest.rsplit(' ', 1)  # 从接收者部分提取时间戳
                    if _is_valid_time_format(time_part):  # 验证时间戳格式
                        username = user_part + ' --> ' + receiver  # 构建完整用户名
                        timestamp = time_part  # 设置时间戳
                        new_format_match = True  # 标记为匹配成功
                except:
                    pass  # 格式不匹配时继续
        
        # 如果匹配成功新格式，或者检测到旧格式（下一行是时间戳）
        if new_format_match or (i + 1 < len(lines) and lines[i + 1].strip().startswith('20')):
            if not new_format_match:  # 如果是旧格式
                username = line  # 当前行是用户名
                timestamp = lines[i + 1].strip()  # 下一行是时间戳
                i += 2  # 跳过两行（用户名和时间戳）
            else:
                i += 1  # 新格式只跳过当前行
            
            # 收集消息内容
            message_content = []  # 存储消息文本内容
            status_flags = []  # 存储状态标识（已读/未读/发送中）
            url_content = []  # 存储URL链接
            
            # 循环收集消息内容，直到遇到新消息开始
            while i < len(lines):
                content_line = lines[i].strip()  # 获取当前内容行
                
                if _is_new_message_start(content_line, i, lines):  # 检查是否新消息开始
                    break  # 如果是新消息，结束当前消息收集
                
                # 收集URL - 以http开头或`http开头的行
                if content_line.startswith('http') or content_line.startswith('`http'):
                    # 提取URL - 去除反引号
                    url = content_line.strip('`')
                    url_content.append(url)  # 添加到URL列表
                    i += 1  # 处理下一行
                    continue  # 跳过本次循环剩余部分
                
                # 跳过系统消息和特殊内容
                if _is_skip_line(content_line):
                    i += 1  # 跳过该行
                    continue  # 继续处理下一行
                
                # 检查状态标识
                if content_line in ['已读', '未读', '发送中']:
                    status_flags.append(content_line)  # 添加到状态列表
                    i += 1  # 处理下一行
                    continue  # 跳过本次循环剩余部分
                
                # 收集非空的消息内容
                if content_line:
                    message_content.append(content_line)  # 添加到消息内容
                
                i += 1  # 处理下一行
            
            # 构建消息字符串
            message_str = '\n'.join(message_content).strip()  # 用换行符连接消息内容
            # 如果有消息内容、状态标识或URL，则创建消息记录
            if message_str or status_flags or url_content:
                message_data = {  # 构建消息数据字典
                    'username': username,  # 用户名
                    'timestamp': timestamp,  # 时间戳
                    'message': message_str,  # 消息内容
                    'status': status_flags[-1] if status_flags else None  # 最后一个状态标识
                }
                
                # 添加URL信息 - 如果有收集到的URL
                if url_content:
                    message_data['urls'] = url_content  # 添加URL列表到消息数据
                
                messages.append(message_data)  # 添加到消息列表
        else:
            i += 1  # 不是消息开始，跳过当前行
    
    return messages  # 返回解析完成的消息列表


if __name__ == "__main__":
    # 主函数 - 当脚本直接运行时执行
    save_folder = "千牛复制数据解析"  # 设置图像保存文件夹
    result = read_clipboard_content(save_folder)  # 读取剪贴板内容
    
    # 解析聊天记录为JSON格式
    chat_json = parse_qianniu_chat_to_json(result['text'])
    
    # 导入json模块用于格式化输出
    import json
    print("原始剪贴板内容:")  # 打印原始内容标题
    print(result)  # 打印剪贴板原始内容
    print("\n解析后的JSON格式:")  # 打印解析结果标题
    print(json.dumps(chat_json, ensure_ascii=False, indent=2))  # 格式化打印JSON结果
