#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
千牛PC端简易Hook获取聊天消息
基于剪贴板监控和UI自动化的替代方案
"""

import time
import json
import os
from datetime import datetime
import threading
import subprocess
import sys

# 添加已有的剪贴板功能
import pyperclip
from PIL import ImageGrab

class SimpleQianNiuHook:
    def __init__(self):
        self.is_running = False
        self.message_callback = None
        self.last_clipboard_text = ""
        self.monitor_thread = None
        self.messages_file = "qianniu_messages.json"
        
    def on_message(self, callback):
        """设置消息回调函数"""
        self.message_callback = callback
    
    def get_clipboard_text(self):
        """获取剪贴板文本"""
        try:
            text = pyperclip.paste()
            return text if text else ""
        except Exception as e:
            print(f"获取剪贴板失败: {e}")
            return ""
    
    def monitor_clipboard(self):
        """监控剪贴板变化"""
        print("开始监控剪贴板，请复制千牛聊天消息...")
        
        while self.is_running:
            try:
                current_text = self.get_clipboard_text()
                
                # 检测新内容
                if current_text and current_text != self.last_clipboard_text:
                    # 检查是否是聊天消息格式
                    if self.is_chat_message_format(current_text):
                        message_data = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'content': current_text,
                            'source': 'clipboard',
                            'type': 'text'
                        }
                        
                        print(f"\n[检测到新消息] {message_data['timestamp']}")
                        print(f"内容: {current_text[:100]}...")
                        
                        if self.message_callback:
                            self.message_callback(message_data)
                        
                        self.save_message(message_data)
                    
                    self.last_clipboard_text = current_text
                
                time.sleep(0.5)  # 降低CPU占用
                
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(1)
    
    def is_chat_message_format(self, text):
        """判断是否是聊天消息格式"""
        # 千牛聊天记录的特征
        lines = text.strip().split('\n')
        
        # 检查是否包含用户名和时间格式
        for line in lines:
            line = line.strip()
            if ('tb' in line and len(line) > 6) or ('syt' in line and len(line) > 6):
                return True
            if '2025-' in line and (' ' in line or ':' in line):
                return True
        
        # 检查是否包含典型的聊天内容
        chat_keywords = ['客服', '亲', '订单', '商品', '价格', '优惠', '发货']
        for keyword in chat_keywords:
            if keyword in text:
                return True
        
        return False
    
    def save_message(self, message_data):
        """保存消息到JSON文件"""
        try:
            # 读取现有数据
            if os.path.exists(self.messages_file):
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            # 添加新消息
            messages.append(message_data)
            
            # 保存回文件
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            print(f"消息已保存到 {self.messages_file}")
        except Exception as e:
            print(f"保存消息失败: {e}")
    
    def simulate_hotkey_copy(self):
        """模拟快捷键复制当前聊天内容"""
        try:
            # 使用PowerShell发送Ctrl+A和Ctrl+C
            ps_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait("^a")
            Start-Sleep -Milliseconds 500
            [System.Windows.Forms.SendKeys]::SendWait("^c")
            Start-Sleep -Milliseconds 500
            '''
            
            subprocess.run(['powershell', '-Command', ps_script], check=True)
            return True
        except Exception as e:
            print(f"模拟快捷键失败: {e}")
            return False
    
    def auto_copy_chat_content(self):
        """自动复制聊天内容"""
        print("正在尝试自动复制聊天内容...")
        
        # 尝试模拟快捷键复制
        if self.simulate_hotkey_copy():
            time.sleep(1)  # 等待复制完成
            current_text = self.get_clipboard_text()
            
            if current_text and self.is_chat_message_format(current_text):
                message_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'content': current_text,
                    'source': 'auto_copy',
                    'type': 'text'
                }
                
                print(f"\n[自动获取聊天内容] {message_data['timestamp']}")
                print(f"内容: {current_text[:100]}...")
                
                if self.message_callback:
                    self.message_callback(message_data)
                
                self.save_message(message_data)
                return True
        
        return False
    
    def start_monitoring(self):
        """开始监控"""
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("剪贴板监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("监控已停止")


def main():
    """主函数"""
    print("=== 简易千牛Hook获取聊天消息 ===")
    print("使用方法:")
    print("1. 打开千牛聊天窗口")
    print("2. 手动复制聊天内容，或按 'c' 自动复制")
    print("3. 程序会自动检测并保存聊天消息")
    print("4. 按 'q' 退出程序")
    print("=" * 40)
    
    # 创建Hook实例
    hook = SimpleQianNiuHook()
    
    # 设置消息处理回调
    def handle_message(message_data):
        print(f"\n[消息处理] 时间: {message_data['timestamp']}")
        print(f"来源: {message_data['source']}")
        print(f"内容预览: {message_data['content'][:50]}...")
    
    hook.on_message(handle_message)
    
    # 启动监控
    hook.start_monitoring()
    
    try:
        while True:
            command = input("\n请输入命令 (c=复制聊天内容, q=退出): ").strip().lower()
            
            if command == 'c':
                hook.auto_copy_chat_content()
            elif command == 'q':
                break
            else:
                print("未知命令，请输入 'c' 或 'q'")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        hook.stop_monitoring()
        print("程序已退出")


if __name__ == "__main__":
    main()