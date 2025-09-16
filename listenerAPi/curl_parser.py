#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CURL命令解析器 - 用于分析和重放HTTP请求
支持验证码图片抓取和请求头分析
"""

import re
import json
import requests
import urllib.parse
from typing import Dict, Any, Optional
import os

class CurlParser:
    def __init__(self):
        self.parsed_data = {}
    
    def parse_curl(self, curl_command: str) -> Dict[str, Any]:
        """解析curl命令为结构化数据"""
        curl_command = curl_command.strip()
        
        # 提取URL
        url_match = re.search(r'"(https?://[^"]+)"', curl_command)
        url = url_match.group(1) if url_match else ""
        
        # 提取请求头
        headers = {}
        header_matches = re.findall(r'-H\s+"([^:]+):\s*([^"]*)"', curl_command)
        for key, value in header_matches:
            headers[key.strip()] = value.strip()
        
        # 提取Cookie
        cookie_str = headers.get('Cookie', '')
        cookies = {}
        if cookie_str:
            for cookie in cookie_str.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key.strip()] = value.strip()
        
        # 提取压缩选项
        compressed = '--compressed' in curl_command
        
        # 提取User-Agent
        user_agent = headers.get('User-Agent', '')
        
        # 提取Referer
        referer = headers.get('Referer', '')
        
        self.parsed_data = {
            'url': url,
            'method': 'GET',  # 默认为GET，可以根据需要扩展
            'headers': headers,
            'cookies': cookies,
            'compressed': compressed,
            'user_agent': user_agent,
            'referer': referer,
            'host': headers.get('Host', urllib.parse.urlparse(url).netloc),
            'raw_command': curl_command
        }
        
        return self.parsed_data
    
    def generate_python_code(self) -> str:
        """生成对应的Python requests代码"""
        if not self.parsed_data:
            return "# 请先解析curl命令"
        
        code = f"""import requests

url = "{self.parsed_data['url']}"

headers = {json.dumps(self.parsed_data['headers'], indent=4, ensure_ascii=False)}

cookies = {json.dumps(self.parsed_data['cookies'], indent=4, ensure_ascii=False)}

response = requests.get(url, headers=headers, cookies=cookies"""
        
        if self.parsed_data['compressed']:
            code += ",
    allow_redirects=True,
    stream=True"
        
        code += ")

print(f"状态码: {response.status_code}")
print(f"内容长度: {len(response.content)} bytes")
print(f"内容类型: {response.headers.get('content-type', 'unknown')}")

# 保存响应内容
with open('response_content', 'wb') as f:
    f.write(response.content)
    print("内容已保存到 response_content")
"""
        return code
    
    def execute_request(self, save_file: bool = True) -> Dict[str, Any]:
        """执行解析后的HTTP请求"""
        if not self.parsed_data:
            return {"error": "请先解析curl命令"}
        
        try:
            response = requests.get(
                self.parsed_data['url'],
                headers=self.parsed_data['headers'],
                cookies=self.parsed_data['cookies'],
                allow_redirects=True,
                stream=True,
                timeout=30
            )
            
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content_length': len(response.content),
                'content_type': response.headers.get('content-type', 'unknown'),
                'url': response.url,
                'encoding': response.encoding
            }
            
            if save_file:
                # 根据内容类型保存文件
                content_type = response.headers.get('content-type', '').lower()
                if 'image' in content_type:
                    ext = 'png' if 'png' in content_type else 'jpg'
                    filename = f"captcha_image.{ext}"
                else:
                    filename = "response_data"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                result['saved_file'] = filename
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_captcha_request(self) -> Dict[str, Any]:
        """分析验证码请求的特征"""
        if not self.parsed_data:
            return {"error": "请先解析curl命令"}
        
        analysis = {
            'request_type': 'captcha_image',
            'target_domain': self.parsed_data['host'],
            'user_agent_info': self._parse_user_agent(self.parsed_data['user_agent']),
            'authentication': {
                'has_dutoken': 'duToken' in self.parsed_data['cookies'],
                'has_auth_token': 'x-auth-token' in self.parsed_data['headers'],
                'auth_token_expiry': self._extract_token_expiry()
            },
            'request_fingerprint': {
                'accept_header': self.parsed_data['headers'].get('Accept'),
                'referer': self.parsed_data['referer'],
                'x_requested_with': self.parsed_data['headers'].get('X-Requested-With')
            }
        }
        
        return analysis
    
    def _parse_user_agent(self, ua: str) -> Dict[str, str]:
        """解析User-Agent信息"""
        parts = {
            'platform': 'Unknown',
            'os_version': 'Unknown',
            'device_model': 'Unknown',
            'browser': 'Unknown'
        }
        
        # 从提供的UA中解析信息
        if 'Android' in ua:
            parts['platform'] = 'Android'
            android_match = re.search(r'Android (\d+)', ua)
            if android_match:
                parts['os_version'] = android_match.group(1)
        
        device_match = re.search(r'; ([^;]+) Build/', ua)
        if device_match:
            parts['device_model'] = device_match.group(1)
        
        if 'Chrome/' in ua:
            chrome_match = re.search(r'Chrome/([\d.]+)', ua)
            if chrome_match:
                parts['browser'] = f"Chrome {chrome_match.group(1)}"
        
        return parts
    
    def _extract_token_expiry(self) -> Optional[str]:
        """提取token过期时间"""
        auth_header = self.parsed_data['headers'].get('x-auth-token', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        try:
            # JWT token解码（简化版本）
            token = auth_header[7:]  # 去掉"Bearer "
            # 这里简化处理，实际应该使用base64解码JWT
            return "需要JWT解码工具"
        except:
            return None
    
    def generate_modified_request(self, modifications: Dict[str, Any]) -> str:
        """生成修改后的curl命令"""
        if not self.parsed_data:
            return ""
        
        # 应用修改
        new_data = self.parsed_data.copy()
        new_data['headers'].update(modifications.get('headers', {}))
        new_data['cookies'].update(modifications.get('cookies', {}))
        
        # 重建curl命令
        curl_parts = [f'curl "{new_data["url"]}"']
        
        for key, value in new_data['headers'].items():
            curl_parts.append(f'-H "{key}: {value}"')
        
        if new_data['compressed']:
            curl_parts.append('--compressed')
        
        return ' \\\n  '.join(curl_parts)

# 使用示例
if __name__ == "__main__":
    # 您提供的curl命令
    sample_curl = '''curl -H "Host: davstatic.dewu.com" -H "Pragma: no-cache" -H "Cache-Control: no-cache" -H "User-Agent: Mozilla/5.0 (Linux; Android 9; ASUS_Z01QD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36" -H "Accept: image/webp,image/apng,image/*,*/*;q=0.8" -H "Referer: https://davstatic.dewu.com/captcha.html" -H "Accept-Language: zh-CN,en-US;q=0.9" -H "Cookie: duToken=e84a16dd6f1bc3f478238daa452eb20e182d01fb71d0f0aa4331d08594fc09b58de68c794fabe74c1dc965d079320d1a2b155dc26b182520c74e80458c8a8e4d1dce67a1d3aae2e7888243c32171b6e0|2640925717|1757904365|63e6060f195c9c7816e560c91a652864bd89bbad|1-0|b9c0d338d9cb188f; dw_edge_er_cookie=082f5357-8d0a-97c9-47e4-61d93b6b95c4; HWWAFSESID=e8f99166fb8d9186312; HWWAFSESTIME=1758001582336; x-auth-token=Bearer eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3NTgwMDE1ODMsImV4cCI6MTc4OTUzNzU4MywiaXNzIjoiZTNhNjRkYTYwZmRjYmNiOSIsInN1YiI6ImUzYTY0ZGE2MGZkY2JjYjkiLCJ1dWlkIjoiZTNhNjRkYTYwZmRjYmNiOSIsInVzZXJJZCI6MjY0MDkyNTcxNywidXNlck5hbWUiOiLkvI3mn5J3dWdoaSIsImlzR3Vlc3QiOmZhbHNlfQ.puTGWP90N3kZrgn7TmTdeJnuPBIbw7nOZftNXEueyTYZbj9dqPClDr8LOLRx89WWOzB3NyYlSArH3RddnnCGMsgiIZTMlMc4NejwaWy8Dt1adLQaIPyncyTTQaQgTZCIO46R8c17OtGHZduUbXe-SLI3JNDeErsYGrHuCEjRLINNUyXhO3JCKNOqEaVS1_fbpR9Tq5Riok4tVjA9Z7qnAIdWhKqkfhdY-G26rNux-cV4J6LMmi9m6xIb1128Mqr1HrnDox7HTi5FPVIYM_5TBfrEH61oQnLDyxJr6kXJobGT39ojMOowuh4YgdkGiq3HaAPkaB6m8kfOCnl1z2VhcQ" -H "X-Requested-With: com.shizhuang.duapp" --compressed "https://davstatic.dewu.com/captcha/blank.png"'''
    
    parser = CurlParser()
    parsed = parser.parse_curl(sample_curl)
    
    print("解析结果:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))
    
    print("\n分析结果:")
    analysis = parser.analyze_captcha_request()
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    print("\nPython代码:")
    print(parser.generate_python_code())