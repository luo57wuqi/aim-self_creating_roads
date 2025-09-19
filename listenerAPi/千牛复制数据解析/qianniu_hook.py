#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千牛PC端Hook获取聊天消息
基于Windows消息钩子和UI自动化技术
"""

import win32gui
import win32con
import win32clipboard as clipboard
import ctypes
from ctypes import wintypes
import time
import json
from datetime import datetime
import os

# Windows API常量
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_COPY = 0x0301
WM_PASTE = 0x0302

class QianNiuHook:
    def __init__(self):
        self.qianniu_hwnd = None
        self.chat_hwnd = None
        self.message_callback = None
        self.is_running = False
        self.last_message = ""
        
    def find_qianniu_window(self):
        """查找千牛主窗口"""
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "千牛" in window_text or "阿里旺旺" in window_text:
                    windows.append((hwnd, window_text))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        
        if windows:
            self.qianniu_hwnd = windows[0][0]
            print(f"找到千牛窗口: {windows[0][1]} (句柄: {self.qianniu_hwnd})")
            return True
        return False
    
    def find_chat_window(self):
        """查找聊天窗口"""
        if not self.qianniu_hwnd:
            return False
            
        def enum_child_callback(hwnd, chat_windows):
            class_name = win32gui.GetClassName(hwnd)
            window_text = win32gui.GetWindowText(hwnd)
            
            # 千牛聊天窗口通常有特定的类名或包含特定文字
            if ("ChatWnd" in class_name or 
                "会话" in window_text or 
                "聊天" in window_text or
                "RichEdit" in class_name):
                chat_windows.append((hwnd, class_name, window_text))
            return True
        
        chat_windows = []
        win32gui.EnumChildWindows(self.qianniu_hwnd, enum_child_callback, chat_windows)
        
        if chat_windows:
            # 通常第一个找到的聊天窗口就是当前活跃的
            self.chat_hwnd = chat_windows[0][0]
            print(f"找到聊天窗口: {chat_windows[0][2]} (句柄: {self.chat_hwnd})")
            return True
        return False
    
    def get_window_text(self, hwnd):
        """获取窗口文本内容"""
        try:
            length = win32gui.SendMessage(hwnd, WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                buffer = win32gui.PyMakeBuffer(length + 1)
                win32gui.SendMessage(hwnd, WM_GETTEXT, length + 1, buffer)
                text = buffer[:length].decode('utf-8', errors='ignore')
                return text
        except Exception as e:
            print(f"获取窗口文本失败: {e}")
        return ""
    
    def monitor_chat_messages(self):
        """监控聊天消息"""
        if not self.chat_hwnd:
            print("未找到聊天窗口")
            return
        
        print("开始监控聊天消息...")
        self.is_running = True
        
        while self.is_running:
            try:
                # 获取当前聊天内容
                current_text = self.get_window_text(self.chat_hwnd)
                
                if current_text and current_text != self.last_message:
                    # 检测到新消息
                    new_message = current_text.replace(self.last_message, "").strip()
                    
                    if new_message and self.message_callback:
                        message_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'content': new_message,
                            'full_content': current_text
                        }
                        self.message_callback(message_data)
                    
                    self.last_message = current_text
                
                time.sleep(0.5)  # 降低CPU占用
                
            except KeyboardInterrupt:
                print("停止监控")
                break
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(1)
    
    def on_message(self, callback):
        """设置消息回调函数"""
        self.message_callback = callback
    
    def start(self):
        """启动Hook"""
        print("正在初始化千牛Hook...")
        
        if not self.find_qianniu_window():
            print("未找到千牛窗口，请确保千牛客户端已启动")
            return False
        
        if not self.find_chat_window():
            print("未找到聊天窗口，请打开一个聊天会话")
            return False
        
        print("千牛Hook初始化成功！")
        return True
    
    def stop(self):
        """停止Hook"""
        self.is_running = False
        print("千牛Hook已停止")


def save_message_to_json(message_data, filename="qianniu_messages.json"):
    """保存消息到JSON文件"""
    try:
        # 读取现有数据
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        else:
            messages = []
        
        # 添加新消息
        messages.append(message_data)
        
        # 保存回文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        print(f"消息已保存到 {filename}")
    except Exception as e:
        print(f"保存消息失败: {e}")


def main():
    """主函数"""
    print("=== 千牛PC端Hook获取聊天消息 ===")
    print("1. 请确保千牛客户端已启动")
    print("2. 请打开一个聊天会话窗口")
    print("3. 按Ctrl+C停止监控")
    print("=" * 40)
    
    # 创建Hook实例
    hook = QianNiuHook()
    
    # 设置消息处理回调
    def handle_message(message_data):
        print(f"\n[新消息] {message_data['timestamp']}")
        print(f"内容: {message_data['content']}")
        
        # 保存到JSON文件
        save_message_to_json(message_data)
    
    hook.on_message(handle_message)
    
    # 启动Hook
    if hook.start():
        try:
            # 开始监控
            hook.monitor_chat_messages()
        except KeyboardInterrupt:
            print("\n正在停止监控...")
        finally:
            hook.stop()
    else:
        print("Hook启动失败，请检查千牛客户端状态")


if __name__ == "__main__":
    main()