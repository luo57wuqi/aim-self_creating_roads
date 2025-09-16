# HTTP抓包分析工具使用指南

## 工具概览

我们为您创建了一套完整的HTTP抓包分析工具，包含以下组件：

1. **curl_parser.py** - CURL命令解析器
2. **captcha_grabber.py** - 验证码图片抓取器
3. **request_manager.py** - 请求数据管理器

## 快速开始

### 1. 分析用户提供的curl命令

```bash
python curl_parser.py "curl -H 'Host: davstatic.dewu.com' ..."
```

### 2. 抓取验证码图片

```bash
# 直接抓取空白验证码
python captcha_grabber.py

# 抓取指定参数的验证码
python captcha_grabber.py --params "type=login&width=120&height=40"

# 批量抓取
python captcha_grabber.py --count 10 --delay 1
```

### 3. 管理抓包数据

```bash
# 启动交互式管理器
python request_manager.py

# 查看统计信息
python -c "from request_manager import RequestManager; print(RequestManager().get_statistics())"
```

## 详细使用说明

### curl_parser.py - CURL命令解析器

#### 功能特性
- 解析curl命令为结构化数据
- 生成可执行的Python代码
- 支持请求重放
- 分析请求头信息

#### 使用示例

```python
from curl_parser import CurlParser

# 解析curl命令
parser = CurlParser()
result = parser.parse_curl_command('curl -H "Host: davstatic.dewu.com" ...')

# 获取Python代码
python_code = parser.generate_python_code(result)
print(python_code)

# 执行请求
response = parser.execute_request(result)
```

### captcha_grabber.py - 验证码图片抓取器

#### 功能特性
- 自动会话管理
- 认证信息保持
- 验证码图片下载
- 批量抓取功能
- 会话持久化

#### 配置说明

编辑文件开头的配置部分：

```python
DEFAULT_CONFIG = {
    'base_url': 'https://davstatic.dewu.com/captcha/',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_Z01QD...',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': 'https://davstatic.dewu.com/captcha.html',
        'X-Requested-With': 'com.shizhuang.duapp'
    },
    'cookies': {
        'duToken': 'your_token_here',
        'x-auth-token': 'Bearer your_jwt_token_here'
    }
}
```

#### 命令行参数

```bash
# 基本使用
python captcha_grabber.py

# 自定义参数
python captcha_grabber.py --params "type=register"

# 批量抓取
python captcha_grabber.py --count 5 --delay 2 --output ./captchas/

# 使用保存的会话
python captcha_grabber.py --session saved_session.json
```

### request_manager.py - 请求数据管理器

#### 功能特性
- 请求数据持久化存储
- 会话管理
- 数据导入导出
- 搜索和过滤
- 统计分析

#### 数据库结构

- `requests` - 存储所有HTTP请求
- `sessions` - 存储会话信息
- `session_requests` - 会话与请求的关联

#### 使用示例

```python
from request_manager import RequestManager

# 创建管理器实例
manager = RequestManager()

# 保存请求
request_data = {
    'url': 'https://davstatic.dewu.com/captcha/blank.png',
    'method': 'GET',
    'headers': {...},
    'cookies': {...}
}

request_hash = manager.save_request(request_data, tags=['captcha'])

# 创建会话
session_id = manager.create_session("Dewu Captcha", "验证码抓取会话")
manager.add_to_session(session_id, [request_hash])

# 导出会话
manager.export_session(session_id, "dewu_captcha_session.json")

# 导入会话
new_session_id = manager.import_session("dewu_captcha_session.json")

# 搜索请求
captcha_requests = manager.search_requests("captcha", field='url')

# 获取统计信息
stats = manager.get_statistics()
```

## 实际应用场景

### 场景1：验证码图片批量收集

```bash
# 步骤1：分析curl命令
python curl_parser.py "curl -H 'Host: davstatic.dewu.com' ..."

# 步骤2：配置抓取器
编辑 captcha_grabber.py 中的 Cookie 和认证信息

# 步骤3：批量抓取
python captcha_grabber.py --count 100 --delay 0.5 --output ./captcha_dataset/

# 步骤4：管理数据
python -c "
from request_manager import RequestManager
m = RequestManager()
session = m.create_session('Dewu Captcha Dataset', '100张验证码图片')
print(f'创建会话ID: {session}')
"
```

### 场景2：API接口测试

```bash
# 使用curl_parser测试不同参数
python curl_parser.py "curl -X POST -d 'type=login' ..."

# 保存测试用例
python -c "
from request_manager import RequestManager
m = RequestManager()
# 保存多个测试用例...
"

# 导出测试套件
python -c "
from request_manager import RequestManager
m = RequestManager()
m.export_session(1, 'api_test_suite.json')
"
```

### 场景3：会话重放

```bash
# 导入历史会话
python -c "
from request_manager import RequestManager
m = RequestManager()
session_id = m.import_session('saved_session.json')
print(f'导入会话: {session_id}')
"

# 使用captcha_grabber重放会话
python captcha_grabber.py --session saved_session.json
```

## 故障排除

### 常见问题

1. **Cookie过期**
   - 更新 captcha_grabber.py 中的 Cookie 信息
   - 重新获取有效的认证token

2. **请求被拒绝**
   - 检查 User-Agent 设置
   - 验证 Referer 和 X-Requested-With 头
   - 确认IP未被限制

3. **数据库错误**
   - 删除 requests.db 重新初始化
   - 检查文件权限

### 调试技巧

```python
# 开启调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看详细请求信息
python curl_parser.py "curl ..." --debug

# 检查数据库内容
python -c "
import sqlite3
conn = sqlite3.connect('requests.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM requests LIMIT 5')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

## 扩展功能

### 添加新的验证码类型支持

编辑 captcha_grabber.py，添加新的验证码类型处理：

```python
# 在 grab_captcha_with_params 函数中添加
if params.get('type') == 'new_type':
    # 自定义处理逻辑
    pass
```

### 集成机器学习预处理

```python
# 在批量抓取后自动预处理
from PIL import Image
import numpy as np

def preprocess_captcha(image_path):
    img = Image.open(image_path)
    # 添加预处理逻辑
    return processed_img
```

## 文件结构

```
workspace/
├── curl_parser.py          # CURL命令解析器
├── captcha_grabber.py      # 验证码图片抓取器
├── request_manager.py      # 请求数据管理器
├── usage_guide.md          # 本使用指南
├── requests.db             # 数据库文件（自动生成）
├── saved_session.json      # 会话文件（自动生成）
└── captchas/              # 验证码图片保存目录
    ├── blank_001.png
    ├── blank_002.png
    └── ...
```

## 下一步建议

1. **验证码识别**：集成OCR或机器学习模型进行验证码识别
2. **自动化测试**：创建完整的API测试套件
3. **数据可视化**：添加请求统计图表
4. **Web界面**：开发基于Flask的Web管理界面

需要任何功能扩展或遇到问题，请随时提问！