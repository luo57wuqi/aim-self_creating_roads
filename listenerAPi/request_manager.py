#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP请求管理器
用于保存、管理和重放抓包数据
"""

import json
import os
import sqlite3
import datetime
from typing import Dict, List, Optional, Any
import hashlib

class RequestManager:
    def __init__(self, db_path: str = "requests.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash TEXT UNIQUE,
                url TEXT,
                method TEXT DEFAULT 'GET',
                headers TEXT,
                cookies TEXT,
                body TEXT,
                timestamp DATETIME,
                response_status INTEGER,
                response_headers TEXT,
                response_body TEXT,
                tags TEXT,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_requests (
                session_id INTEGER,
                request_id INTEGER,
                order_index INTEGER,
                FOREIGN KEY (session_id) REFERENCES sessions (id),
                FOREIGN KEY (request_id) REFERENCES requests (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_request(self, request_data: Dict[str, Any], 
                    response_data: Optional[Dict[str, Any]] = None,
                    tags: List[str] = None, notes: str = "") -> str:
        """保存请求到数据库"""
        
        # 生成请求哈希
        request_str = json.dumps(request_data, sort_keys=True)
        request_hash = hashlib.md5(request_str.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO requests 
            (hash, url, method, headers, cookies, body, timestamp, 
             response_status, response_headers, response_body, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_hash,
            request_data.get('url', ''),
            request_data.get('method', 'GET'),
            json.dumps(request_data.get('headers', {}), ensure_ascii=False),
            json.dumps(request_data.get('cookies', {}), ensure_ascii=False),
            request_data.get('body', ''),
            datetime.datetime.now(),
            response_data.get('status_code') if response_data else None,
            json.dumps(response_data.get('headers', {}), ensure_ascii=False) if response_data else None,
            response_data.get('body', '') if response_data else None,
            json.dumps(tags or [], ensure_ascii=False),
            notes
        ))
        
        conn.commit()
        conn.close()
        
        return request_hash
    
    def get_request(self, request_hash: str) -> Optional[Dict[str, Any]]:
        """根据哈希获取请求"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM requests WHERE hash = ?
        ''', (request_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'hash': row[1],
                'url': row[2],
                'method': row[3],
                'headers': json.loads(row[4]) if row[4] else {},
                'cookies': json.loads(row[5]) if row[5] else {},
                'body': row[6],
                'timestamp': row[7],
                'response_status': row[8],
                'response_headers': json.loads(row[9]) if row[9] else {},
                'response_body': row[10],
                'tags': json.loads(row[11]) if row[11] else [],
                'notes': row[12]
            }
        return None
    
    def list_requests(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """列出所有请求"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM requests 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            requests.append({
                'id': row[0],
                'hash': row[1],
                'url': row[2],
                'method': row[3],
                'timestamp': row[7],
                'response_status': row[8],
                'tags': json.loads(row[11]) if row[11] else []
            })
        
        return requests
    
    def create_session(self, name: str, description: str = "") -> int:
        """创建会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        cursor.execute('''
            INSERT INTO sessions (name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (name, description, now, now))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def add_to_session(self, session_id: int, request_hashes: List[str]):
        """将请求添加到会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取请求ID
        placeholders = ','.join(['?' for _ in request_hashes])
        cursor.execute(f'''
            SELECT id, hash FROM requests WHERE hash IN ({placeholders})
        ''', request_hashes)
        
        request_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        # 添加请求到会话
        for order_index, hash_value in enumerate(request_hashes):
            if hash_value in request_map:
                cursor.execute('''
                    INSERT INTO session_requests (session_id, request_id, order_index)
                    VALUES (?, ?, ?)
                ''', (session_id, request_map[hash_value], order_index))
        
        # 更新会话时间
        cursor.execute('''
            UPDATE sessions SET updated_at = ? WHERE id = ?
        ''', (datetime.datetime.now(), session_id))
        
        conn.commit()
        conn.close()
    
    def export_session(self, session_id: int, filename: str):
        """导出会话为JSON文件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取会话信息
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session_row = cursor.fetchone()
        
        if not session_row:
            conn.close()
            return False
        
        # 获取会话中的请求
        cursor.execute('''
            SELECT r.* FROM requests r
            JOIN session_requests sr ON r.id = sr.request_id
            WHERE sr.session_id = ?
            ORDER BY sr.order_index
        ''', (session_id,))
        
        rows = cursor.fetchall()
        
        session_data = {
            'session_info': {
                'id': session_row[0],
                'name': session_row[1],
                'description': session_row[2],
                'created_at': session_row[3],
                'updated_at': session_row[4]
            },
            'requests': []
        }
        
        for row in rows:
            request_data = {
                'url': row[2],
                'method': row[3],
                'headers': json.loads(row[4]) if row[4] else {},
                'cookies': json.loads(row[5]) if row[5] else {},
                'body': row[6],
                'response_status': row[8],
                'response_headers': json.loads(row[9]) if row[9] else {},
                'response_body': row[10],
                'tags': json.loads(row[11]) if row[11] else [],
                'notes': row[12]
            }
            session_data['requests'].append(request_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        conn.close()
        return True
    
    def import_session(self, filename: str) -> Optional[int]:
        """从JSON文件导入会话"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 创建会话
            session_info = session_data['session_info']
            session_id = self.create_session(
                session_info['name'],
                session_info.get('description', '')
            )
            
            # 保存请求
            request_hashes = []
            for req in session_data['requests']:
                request_hash = self.save_request(req)
                request_hashes.append(request_hash)
            
            # 添加到会话
            self.add_to_session(session_id, request_hashes)
            
            return session_id
            
        except Exception as e:
            print(f"导入失败: {e}")
            return None
    
    def search_requests(self, query: str, field: str = 'url') -> List[Dict[str, Any]]:
        """搜索请求"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql_query = f'''
            SELECT * FROM requests 
            WHERE {field} LIKE ? 
            ORDER BY timestamp DESC
        '''
        
        cursor.execute(sql_query, (f'%{query}%',))
        rows = cursor.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            requests.append({
                'id': row[0],
                'hash': row[1],
                'url': row[2],
                'method': row[3],
                'timestamp': row[7],
                'response_status': row[8],
                'tags': json.loads(row[11]) if row[11] else []
            })
        
        return requests
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 请求统计
        cursor.execute('SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM requests')
        count, min_time, max_time = cursor.fetchone()
        
        # 域名统计
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN url LIKE '%://%' THEN SUBSTR(url, INSTR(url, '://') + 3, 
                        INSTR(SUBSTR(url, INSTR(url, '://') + 3), '/') - 1)
                    ELSE 'unknown'
                END as domain,
                COUNT(*) as count
            FROM requests
            GROUP BY domain
            ORDER BY count DESC
        ''')
        
        domains = cursor.fetchall()
        
        # 状态码统计
        cursor.execute('''
            SELECT response_status, COUNT(*) 
            FROM requests 
            WHERE response_status IS NOT NULL
            GROUP BY response_status
            ORDER BY count DESC
        ''')
        
        status_codes = cursor.fetchall()
        
        # 会话统计
        cursor.execute('SELECT COUNT(*) FROM sessions')
        session_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_requests': count or 0,
            'date_range': {
                'start': min_time,
                'end': max_time
            },
            'domains': dict(domains),
            'status_codes': dict(status_codes),
            'total_sessions': session_count
        }

def main():
    """主函数 - 演示功能"""
    manager = RequestManager()
    
    # 示例：保存用户提供的curl请求
    sample_request = {
        'url': 'https://davstatic.dewu.com/captcha/blank.png',
        'method': 'GET',
        'headers': {
            'Host': 'davstatic.dewu.com',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_Z01QD Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.70 Mobile Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://davstatic.dewu.com/captcha.html',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'X-Requested-With': 'com.shizhuang.duapp'
        },
        'cookies': {
            'duToken': 'e84a16dd6f1bc3f478238daa452eb20e182d01fb71d0f0aa4331d08594fc09b58de68c794fabe74c1dc965d079320d1a2b155dc26b182520c74e80458c8a8e4d1dce67a1d3aae2e7888243c32171b6e0|2640925717|1757904365|63e6060f195c9c7816e560c91a652864bd89bbad|1-0|b9c0d338d9cb188f',
            'dw_edge_er_cookie': '082f5357-8d0a-97c9-47e4-61d93b6b95c4',
            'HWWAFSESID': 'e8f99166fb8d9186312',
            'HWWAFSESTIME': '1758001582336',
            'x-auth-token': 'Bearer eyJhbGciOiJSUzI1NiJ9...'
        }
    }
    
    # 保存请求
    request_hash = manager.save_request(
        sample_request,
        tags=['captcha', 'dewu', 'android'],
        notes="用户提供的验证码抓取请求"
    )
    
    # 创建会话
    session_id = manager.create_session(
        "Dewu Captcha Session",
        "验证码图片抓取会话"
    )
    
    manager.add_to_session(session_id, [request_hash])
    
    # 显示统计
    stats = manager.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()