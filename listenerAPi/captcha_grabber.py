#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证码图片抓取器
基于提供的curl命令实现自动化验证码获取
"""

import requests
import json
import os
import time
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional

class CaptchaGrabber:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://davstatic.dewu.com"
        self.captcha_urls = []
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_Z01QD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Requested-With': 'com.shizhuang.duapp'
        })
    
    def set_auth_headers(self, cookies: Dict[str, str], token: str = None):
        """设置认证信息"""
        # 设置cookies
        for key, value in cookies.items():
            self.session.cookies.set(key, value)
        
        # 设置认证token
        if token:
            self.session.headers['x-auth-token'] = f'Bearer {token}'
    
    def grab_captcha_image(self, image_url: str, save_path: str = None) -> Dict[str, any]:
        """抓取验证码图片"""
        try:
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()
            
            if save_path is None:
                # 自动生成文件名
                timestamp = int(time.time())
                filename = f"captcha_{timestamp}.png"
                save_path = os.path.join("captures", filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return {
                'success': True,
                'file_path': save_path,
                'file_size': len(response.content),
                'content_type': response.headers.get('content-type'),
                'url': image_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': image_url
            }
    
    def grab_blank_captcha(self) -> Dict[str, any]:
        """抓取空白验证码图片"""
        url = f"{self.base_url}/captcha/blank.png"
        return self.grab_captcha_image(url)
    
    def grab_captcha_with_params(self, **params) -> Dict[str, any]:
        """带参数的验证码抓取"""
        # 构建URL参数
        url = f"{self.base_url}/captcha"
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
        
        return self.grab_captcha_image(url)
    
    def analyze_response_headers(self, image_url: str) -> Dict[str, str]:
        """分析响应头信息"""
        try:
            response = self.session.head(image_url, timeout=5)
            return dict(response.headers)
        except Exception as e:
            return {'error': str(e)}
    
    def batch_grab_captchas(self, urls: List[str], delay: float = 1.0) -> List[Dict[str, any]]:
        """批量抓取验证码"""
        results = []
        for url in urls:
            result = self.grab_captcha_image(url)
            results.append(result)
            if delay > 0:
                time.sleep(delay)
        return results
    
    def generate_captcha_urls(self, base_pattern: str, count: int = 10) -> List[str]:
        """生成验证码URL列表"""
        urls = []
        for i in range(count):
            timestamp = int(time.time() * 1000) + i
            url = base_pattern.replace('{timestamp}', str(timestamp))
            urls.append(url)
        return urls
    
    def save_session_info(self, filename: str = "session_info.json"):
        """保存会话信息"""
        session_info = {
            'cookies': dict(self.session.cookies),
            'headers': dict(self.session.headers),
            'timestamp': int(time.time())
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)
    
    def load_session_info(self, filename: str = "session_info.json") -> bool:
        """加载会话信息"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                session_info = json.load(f)
            
            # 恢复cookies
            for key, value in session_info.get('cookies', {}).items():
                self.session.cookies.set(key, value)
            
            # 恢复headers
            for key, value in session_info.get('headers', {}).items():
                self.session.headers[key] = value
            
            return True
        except Exception as e:
            print(f"加载会话信息失败: {e}")
            return False
    
    def get_captcha_stats(self) -> Dict[str, any]:
        """获取验证码抓取统计"""
        captures_dir = "captures"
        if not os.path.exists(captures_dir):
            return {'total_captures': 0, 'files': []}
        
        files = [f for f in os.listdir(captures_dir) if f.startswith('captcha_')]
        total_size = 0
        
        for file in files:
            file_path = os.path.join(captures_dir, file)
            total_size += os.path.getsize(file_path)
        
        return {
            'total_captures': len(files),
            'total_size_bytes': total_size,
            'files': sorted(files),
            'average_size': total_size / len(files) if files else 0
        }

# 预设配置
DEFAULT_CONFIG = {
    'base_url': 'https://davstatic.dewu.com',
    'captcha_endpoints': [
        '/captcha/blank.png',
        '/captcha/image',
        '/captcha/slide',
        '/captcha/puzzle'
    ],
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_Z01QD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,en-US;q=0.9',
        'X-Requested-With': 'com.shizhuang.duapp',
        'Referer': 'https://davstatic.dewu.com/captcha.html'
    },
    'cookies': {
        'duToken': 'e84a16dd6f1bc3f478238daa452eb20e182d01fb71d0f0aa4331d08594fc09b58de68c794fabe74c1dc965d079320d1a2b155dc26b182520c74e80458c8a8e4d1dce67a1d3aae2e7888243c32171b6e0|2640925717|1757904365|63e6060f195c9c7816e560c91a652864bd89bbad|1-0|b9c0d338d9cb188f',
        'dw_edge_er_cookie': '082f5357-8d0a-97c9-47e4-61d93b6b95c4',
        'HWWAFSESID': 'e8f99166fb8d9186312',
        'HWWAFSESTIME': '1758001582336'
    },
    'auth_token': 'eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3NTgwMDE1ODMsImV4cCI6MTc4OTUzNzU4MywiaXNzIjoiZTNhNjRkYTYwZmRjYmNiOSIsInN1YiI6ImUzYTY0ZGE2MGZkY2JjYjkiLCJ1dWlkIjoiZTNhNjRkYTYwZmRjYmNiOSIsInVzZXJJZCI6MjY0MDkyNTcxNywidXNlck5hbWUiOiLkvI3mn5J3dWdoaSIsImlzR3Vlc3QiOmZhbHNlfQ.puTGWP90N3kZrgn7TmTdeJnuPBIbw7nOZftNXEueyTYZbj9dqPClDr8LOLRx89WWOzB3NyYlSArH3RddnnCGMsgiIZTMlMc4NejwaWy8Dt1adLQaIPyncyTTQaQgTZCIO46R8c17OtGHZduUbXe-SLI3JNDeErsYGrHuCEjRLINNUyXhO3JCKNOqEaVS1_fbpR9Tq5Riok4tVjA9Z7qnAIdWhKqkfhdY-G26rNux-cV4J6LMmi9m6xIb1128Mqr1HrnDox7HTi5FPVIYM_5TBfrEH61oQnLDyxJr6kXJobGT39ojMOowuh4YgdkGiq3HaAPkaB6m8kfOCnl1z2VhcQ'
}

def main():
    """主函数 - 演示验证码抓取"""
    grabber = CaptchaGrabber()
    
    # 设置认证信息
    grabber.set_auth_headers(
        cookies=DEFAULT_CONFIG['cookies'],
        token=DEFAULT_CONFIG['auth_token']
    )
    
    print("=== 验证码图片抓取器 ===")
    print("1. 抓取空白验证码")
    print("2. 批量抓取测试")
    print("3. 查看统计信息")
    print("4. 保存会话")
    
    choice = input("请选择操作 (1-4): ").strip()
    
    if choice == '1':
        result = grabber.grab_blank_captcha()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif choice == '2':
        urls = grabber.generate_captcha_urls(
            "https://davstatic.dewu.com/captcha/blank.png?t={timestamp}",
            count=5
        )
        results = grabber.batch_grab_captchas(urls, delay=1)
        for i, result in enumerate(results, 1):
            print(f"抓取 {i}: {result}")
    
    elif choice == '3':
        stats = grabber.get_captcha_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif choice == '4':
        grabber.save_session_info()
        print("会话信息已保存")

if __name__ == "__main__":
    main()