#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千牛PC端Hook获取聊天消息
基于Python标准库和剪贴板监控
无需额外依赖
"""

import subprocess
import time
import json
from datetime import datetime
import os
import ctypes
from ctypes import wintypes
import threading

try:
    # 尝试使用标准库中的ctypes来获取窗口信息
    import ctypes
    from ctypes import wintypes
    
    # Windows API常量
    WM_GETTEXT = 0x000D
    WM_GETTEXTLENGTH = 0x000E
    
    # 定义Windows API函数
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    # 获取窗口文本长度
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.SendMessageW.restype = wintypes.LPARAM
    
    # 枚举窗口
    user32.EnumWindows.argtypes = [ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
    user32.EnumWindows.restype = ctypes.c_bool
    
    # 获取窗口文本
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    
    # 获取窗口类名
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    
    # 检查窗口是否可见
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = ctypes.c_bool
    
    # 检查窗口是否启用
    user32.IsWindowEnabled.argtypes = [wintypes.HWND]
    user32.IsWindowEnabled.restype = ctypes.c_bool
    
    WINDOWS_API_AVAILABLE = True
    print("✅ Windows API (通过ctypes) 可用")
    
except Exception as e:
    WINDOWS_API_AVAILABLE = False
    print(f"⚠️ Windows API不可用: {e}")


class QianNiuHookStd:
    def __init__(self):
        self.qianniu_hwnd = None
        self.chat_hwnd = None
        self.message_callback = None
        self.is_running = False
        self.last_message = ""
        self.monitoring_thread = None
        
    def find_qianniu_window_ctypes(self):
        """使用ctypes查找千牛窗口"""
        if not WINDOWS_API_AVAILABLE:
            return False
            
        qianniu_windows = []
        
        def enum_window_callback(hwnd, lparam):
            if user32.IsWindowVisible(hwnd) and user32.IsWindowEnabled(hwnd):
                # 获取窗口文本
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    window_text = buffer.value
                    
                    if "千牛" in window_text or "阿里旺旺" in window_text:
                        qianniu_windows.append((hwnd, window_text))
            return True
        
        # 创建回调函数
        enum_func = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(enum_window_callback)
        user32.EnumWindows(enum_func, 0)
        
        if qianniu_windows:
            self.qianniu_hwnd = qianniu_windows[0][0]
            print(f"找到千牛窗口: {qianniu_windows[0][1]} (句柄: {self.qianniu_hwnd})")
            return True
        return False
    
    def find_qianniu_window_tasklist(self):
        """使用tasklist命令查找千牛进程"""
        try:
            # 执行tasklist命令
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq QianNiu.exe'], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if 'QianNiu.exe' in result.stdout:
                print("✅ 检测到千牛进程 (QianNiu.exe)")
                return True
            else:
                # 尝试其他可能的进程名
                result = subprocess.run(['tasklist', '/FI', 'WINDOWTITLE eq 千牛'], 
                                      capture_output=True, text=True, encoding='utf-8')
                if '千牛' in result.stdout:
                    print("✅ 检测到千牛进程")
                    return True
            return False
        except Exception as e:
            print(f"⚠️ 使用tasklist检测失败: {e}")
            return False
    
    def find_chat_window_ctypes(self):
        """使用ctypes查找聊天窗口"""
        if not WINDOWS_API_AVAILABLE or not self.qianniu_hwnd:
            return False
        
        chat_windows = []
        
        def enum_child_callback(hwnd, lparam):
            # 获取窗口类名
            class_buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value
            
            # 获取窗口文本
            text_length = user32.GetWindowTextLengthW(hwnd)
            if text_length > 0:
                text_buffer = ctypes.create_unicode_buffer(text_length + 1)
                user32.GetWindowTextW(hwnd, text_buffer, text_length + 1)
                window_text = text_buffer.value
            else:
                window_text = ""
            
            # 检查是否是聊天窗口
            if ("ChatWnd" in class_name or 
                "会话" in window_text or 
                "聊天" in window_text or
                "RichEdit" in class_name or
                "Edit" in class_name):
                chat_windows.append((hwnd, class_name, window_text))
            
            return True
        
        # 枚举子窗口
        enum_func = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(enum_child_callback)
        user32.EnumChildWindows(self.qianniu_hwnd, enum_func, 0)
        
        if chat_windows:
            self.chat_hwnd = chat_windows[0][0]
            print(f"找到聊天窗口: {chat_windows[0][2]} (句柄: {self.chat_hwnd})")
            return True
        return False
    
    def get_window_text_ctypes(self, hwnd):
        """使用ctypes获取窗口文本"""
        if not WINDOWS_API_AVAILABLE:
            return ""
        
        try:
            # 获取文本长度
            length = user32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                # 创建缓冲区
                buffer = ctypes.create_unicode_buffer(length + 1)
                # 获取文本
                user32.SendMessageW(hwnd, WM_GETTEXT, length + 1, ctypes.addressof(buffer))
                return buffer.value
        except Exception as e:
            print(f"获取窗口文本失败: {e}")
        return ""
    
    def get_clipboard_text(self):
        """获取剪贴板文本"""
        try:
            # 使用PowerShell获取剪贴板内容
            result = subprocess.run(
                ['powershell', '-Command', 'Get-Clipboard'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"获取剪贴板失败: {e}")
            return ""
    
    def monitor_chat_messages(self):
        """监控聊天消息"""
        print("开始监控聊天消息...")
        
        # 尝试使用ctypes获取窗口文本
        if WINDOWS_API_AVAILABLE and self.chat_hwnd:
            print("使用Windows API监控窗口文本...")
            self._monitor_window_text()
        else:
            print("使用剪贴板监控模式...")
            self._monitor_clipboard()
    
    def _monitor_window_text(self):
        """监控窗口文本"""
        if not self.chat_hwnd:
            print("未找到聊天窗口")
            return
        
        print("正在监控窗口文本变化...")
        self.is_running = True
        
        while self.is_running:
            try:
                current_text = self.get_window_text_ctypes(self.chat_hwnd)
                
                if current_text and current_text != self.last_message:
                    # 检测新消息
                    new_message = current_text.replace(self.last_message, "").strip()
                    
                    if new_message and self.message_callback:
                        message_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'content': new_message,
                            'full_content': current_text,
                            'source': 'window_text',
                            'type': 'new_message'
                        }
                        self.message_callback(message_data)
                    
                    self.last_message = current_text
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("停止监控")
                break
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(1)
    
    def _monitor_clipboard(self):
        """监控剪贴板"""
        print("正在监控剪贴板变化...")
        self.is_running = True
        
        while self.is_running:
            try:
                current_clipboard = self.get_clipboard_text()
                
                if current_clipboard and current_clipboard != self.last_message:
                    # 检查是否是千牛聊天消息格式
                    if self._is_qianniu_chat_format(current_clipboard):
                        message_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'content': current_clipboard,
                            'full_content': current_clipboard,
                            'source': 'clipboard',
                            'type': 'qianniu_chat'
                        }
                        
                        if self.message_callback:
                            self.message_callback(message_data)
                    
                    self.last_message = current_clipboard
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("停止监控")
                break
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(1)
    
    def _is_qianniu_chat_format(self, text):
        """检查是否是千牛聊天格式"""
        # 千牛聊天消息的特征
        indicators = [
            'tb' in text.lower(),  # 淘宝
            'syt' in text.lower(),  # 系统消息
            ':' in text,  # 时间格式
            '2024' in text or '2025' in text,  # 年份
            len(text) > 20  # 消息长度
        ]
        
        # 如果包含多个特征，则认为是聊天消息
        return sum(indicators) >= 3
    
    def find_qianniu_window(self):
        """查找千牛窗口（综合方法）"""
        # 优先使用ctypes方法
        if WINDOWS_API_AVAILABLE:
            if self.find_qianniu_window_ctypes():
                return True
        
        # 使用tasklist方法
        return self.find_qianniu_window_tasklist()
    
    def find_chat_window(self):
        """查找聊天窗口"""
        if WINDOWS_API_AVAILABLE:
            return self.find_chat_window_ctypes()
        return False
    
    def on_message(self, callback):
        """设置消息回调函数"""
        self.message_callback = callback
    
    def start(self):
        """启动Hook"""
        print("正在初始化千牛Hook...")
        
        if not self.find_qianniu_window():
            print("未找到千牛窗口，请确保千牛客户端已启动")
            return False
        
        if WINDOWS_API_AVAILABLE:
            if not self.find_chat_window():
                print("未找到聊天窗口，将使用剪贴板监控模式")
        
        print("千牛Hook初始化成功！")
        return True
    
    def stop(self):
        """停止Hook"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("千牛Hook已停止")
    
    def start_monitoring(self):
        """开始监控（在新线程中）"""
        self.monitoring_thread = threading.Thread(target=self.monitor_chat_messages)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()


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


def interactive_mode():
    """交互模式"""
    print("=== 千牛PC端Hook获取聊天消息 ===")
    print("1. 请确保千牛客户端已启动")
    print("2. 请打开一个聊天会话窗口")
    print("3. 按Ctrl+C停止监控")
    print("4. 输入 'c' 复制当前剪贴板内容")
    print("5. 输入 'h' 显示帮助")
    print("=" * 40)
    
    # 创建Hook实例
    hook = QianNiuHookStd()
    
    # 设置消息处理回调
    def handle_message(message_data):
        print(f"\n[新消息] {message_data['timestamp']}")
        print(f"来源: {message_data['source']}")
        print(f"类型: {message_data['type']}")
        print(f"内容: {message_data['content'][:100]}...")
        
        # 保存到JSON文件
        save_message_to_json(message_data)
    
    hook.on_message(handle_message)
    
    # 启动Hook
    if hook.start():
        # 开始监控
        hook.start_monitoring()
        
        try:
            while True:
                user_input = input("\n输入命令 (h帮助, c复制, q退出): ").strip().lower()
                
                if user_input == 'h':
                    print("命令帮助:")
                    print("  h - 显示帮助")
                    print("  c - 复制当前剪贴板内容")
                    print("  q - 退出程序")
                
                elif user_input == 'c':
                    clipboard_text = hook.get_clipboard_text()
                    if clipboard_text:
                        print(f"剪贴板内容: {clipboard_text[:100]}...")
                        # 手动触发消息处理
                        message_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'content': clipboard_text,
                            'full_content': clipboard_text,
                            'source': 'manual_copy',
                            'type': 'manual'
                        }
                        handle_message(message_data)
                    else:
                        print("剪贴板为空")
                
                elif user_input == 'q':
                    break
                
                else:
                    print("未知命令，输入'h'查看帮助")
        
        except KeyboardInterrupt:
            print("\n收到中断信号，正在停止...")
        
        finally:
            hook.stop()


def main():
    """主函数"""
    try:
        interactive_mode()
    except Exception as e:
        print(f"程序运行出错: {e}")
        print("正在尝试简化模式...")
        # 这里可以添加简化模式


if __name__ == "__main__":
    main()