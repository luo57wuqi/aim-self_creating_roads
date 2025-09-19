# readcliper.py 功能介绍

## 项目概述
`readcliper.py` 是一个用于读取剪贴板内容并解析千牛聊天记录的 Python 工具。

## 功能架构图

```mermaid
graph TB
    A[开始] --> B{剪贴板是否有内容?}
    B -->|是| C[读取剪贴板内容]
    B -->|否| D[抛出异常]
    
    C --> E[分离文本和图像]
    E --> F[保存图像到文件夹]
    E --> G[提取文本内容]
    
    G --> H{文本是否为空?}
    H -->|否| I[解析千牛聊天记录]
    H -->|是| J[返回空列表]
    
    I --> K[按行分割文本]
    K --> L[遍历每一行]
    
    L --> M{是否新消息开始?}
    M -->|是| N[提取用户名和时间戳]
    M -->|否| O[跳过或收集内容]
    
    N --> P[收集消息内容]
    P --> Q[提取URL链接]
    Q --> R[处理状态标识]
    R --> S[构建消息对象]
    
    O --> L
    S --> T[添加到消息列表]
    T --> U{还有更多行?}
    U -->|是| L
    U -->|否| V[返回JSON格式结果]
    
    V --> W[输出结果]
    
    style A fill:#e1f5fe
    style V fill:#c8e6c9
    style D fill:#ffcdd2
```

## 核心功能模块

### 1. 剪贴板读取模块
```mermaid
graph LR
    A[read_clipboard_content] --> B[_read_clipboard_text]
    A --> C[_read_clipboard_image]
    
    B --> D[pyperclip.paste]
    C --> E[ImageGrab.grabclipboard]
    
    E --> F{获取到图像?}
    F -->|是| G[生成时间戳文件名]
    F -->|否| H[返回None]
    
    G --> I[保存PNG图像]
    
    style A fill:#fff3e0
```

### 2. 聊天记录解析模块
```mermaid
graph TD
    A[parse_qianniu_chat_to_json] --> B[分割文本为行数组]
    
    B --> C[初始化消息列表]
    C --> D[设置行索引i=0]
    
    D --> E{遍历所有行}
    E --> F[去除行首尾空白]
    
    F --> G{行是否为空?}
    G -->|是| H[i++跳过]
    G -->|否| I{检查特殊内容}
    
    I --> J[撤回消息处理]
    I --> K[新消息开始检测]
    I --> L[URL提取]
    I --> M[状态标识处理]
    
    K --> N{匹配成功?}
    N -->|是| O[提取用户名和时间]
    N -->|否| P[继续下一行]
    
    O --> Q[收集消息内容]
    Q --> R[构建消息对象]
    R --> S[添加到列表]
    
    style A fill:#f3e5f5
```

## 消息格式识别

```mermaid
graph TD
    A[输入行文本] --> B[_is_new_message_start]
    
    B --> C{检查撤回消息}
    C -->|是| D[返回True]
    
    C -->|否| E[_extract_username_timestamp]
    E --> F{正则匹配时间戳}
    F -->|成功| G[返回用户名和时间]
    F -->|失败| H[检查其他格式]
    
    H --> I{检查箭头格式}
    I -->|匹配| J[提取发送者和接收者]
    I -->|不匹配| K[检查旧格式]
    
    K --> L{下一行是否时间戳}
    L -->|是| M[返回True]
    L -->|否| N[返回False]
    
    style B fill:#e8f5e8
```

## 内容过滤机制

```mermaid
graph LR
    A[输入内容行] --> B[_is_skip_line]
    
    B --> C{空行?}
    C -->|是| D[跳过]
    
    C -->|否| E{URL链接?}
    E -->|是| F[收集到URL列表]
    
    E -->|否| G{价格符号?}
    G -->|是| H[跳过]
    
    G -->|否| I{系统关键词?}
    I -->|是| J[跳过]
    I -->|否| K{状态标识?}
    
    K -->|是| L[收集到状态列表]
    K -->|否| M[添加到消息内容]
    
    style B fill:#fff8e1
```

## 输出数据结构

```mermaid
graph TD
    A[消息对象] --> B[username: 用户名]
    A --> C[timestamp: 时间戳]
    A --> D[message: 消息内容]
    A --> E[status: 消息状态]
    A --> F[urls: URL列表]
    
    G[最终输出] --> H[JSON格式数组]
    H --> I[每个元素是一个消息对象]
    
    style A fill:#e3f2fd
```

## 使用示例

### 基本使用流程
```mermaid
sequenceDiagram
    participant User
    participant Script
    participant Clipboard
    participant Parser
    
    User->>Script: 运行脚本
    Script->>Clipboard: 读取剪贴板内容
    Clipboard-->>Script: 返回文本和图像
    Script->>Parser: 传入文本内容
    Parser->>Parser: 解析千牛聊天记录
    Parser-->>Script: 返回JSON格式数据
    Script-->>User: 显示解析结果
```

### 支持的聊天记录格式

1. **标准格式**:
   ```
   用户名
   2024-01-15 14:30:25
   消息内容
   已读
   ```

2. **紧凑格式**:
   ```
   用户名2024-01-15 14:30:25
   消息内容
   ```

3. **转交格式**:
   ```
   用户A --> 用户B 2024-01-15 14:30:25
   消息内容
   ```

4. **包含URL**:
   ```
   用户名2024-01-15 14:30:25
   消息内容
   http://example.com
   已读
   ```

## 文件结构

```mermaid
graph TD
    A[readcliper.py] --> B[剪贴板读取功能]
    A --> C[聊天记录解析功能]
    A --> D[主程序入口]
    
    B --> B1[_read_clipboard_text]
    B --> B2[_read_clipboard_image]
    
    C --> C1[_is_valid_time_format]
    C --> C2[_extract_username_timestamp]
    C --> C3[_is_new_message_start]
    C --> C4[_is_skip_line]
    
    D --> E[读取剪贴板]
    D --> F[解析聊天记录]
    D --> G[输出JSON结果]
```

## 安装依赖

```bash
pip install pyperclip pillow pywin32
```

## 运行方式

```bash
python readcliper.py
```

## 注意事项

1. **图像保存**: 剪贴板中的图像会自动保存到指定文件夹
2. **文本编码**: 支持中文和特殊字符处理
3. **格式兼容**: 支持多种千牛聊天记录格式
4. **错误处理**: 包含完善的异常处理机制
5. **URL提取**: 自动识别和提取消息中的URL链接