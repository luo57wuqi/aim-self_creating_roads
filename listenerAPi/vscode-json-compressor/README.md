# JSON Compressor - VSCode插件

一个简单实用的VSCode插件，用于将多行JSON对象压缩成单行格式，快捷键 **Alt+L**。

## 🚀 功能特点

- **一键压缩**：选中JSON文本后按 **Alt+L** 即可压缩
- **智能识别**：自动识别和解析JSON对象
- **格式保留**：保持JSON数据完整性，仅去除换行和多余空格
- **支持选择**：可选中部分文本压缩，不选中则压缩整个文件

## 📦 安装方法

### 方法1：本地安装（推荐）
1. 打开VSCode
2. 按 `Ctrl+Shift+P` 打开命令面板
3. 输入 `Extensions: Install from VSIX`
4. 选择本插件目录下的 `.vsix` 文件（需要先打包）

### 方法2：开发模式安装
1. 打开VSCode
2. 按 `Ctrl+Shift+P` 打开命令面板
3. 输入 `Developer: Install Extension from Location`
4. 选择插件目录路径

### 方法3：直接复制使用
1. 复制 `extension.js` 和 `package.json` 到你的插件目录
2. 重启VSCode即可使用

## 🎯 使用方法

### 示例
**压缩前：**
```json
{
  "268_BSL00218精选": 35,
  "268_BSL00218想要": 3000,
  "269_BLJ05036已买": 56,
  "269_BLJ05036精选": 23,
  "269_BLJ05036想要": 296,
  "270_BLJ02798已买": 34,
  "270_BLJ02798精选": 13,
  "270_BLJ02798想要": 266
}
```

**压缩后：**
```json
{"268_BSL00218精选":35,"268_BSL00218想要":3000,"269_BLJ05036已买":56,"269_BLJ05036精选":23,"269_BLJ05036想要":296,"270_BLJ02798已买":34,"270_BLJ02798精选":13,"270_BLJ02798想要":266}
```

### 操作步骤
1. **打开**包含JSON的代码文件
2. **选择**要压缩的JSON文本（可选，不选则压缩整个文件）
3. **按 Alt+L** 或使用命令面板执行 `压缩JSON对象`
4. **完成**JSON自动压缩为一行

## ⚙️ 命令
- 命令：`json-compressor.compress`
- 标题：压缩JSON对象
- 快捷键：`Alt+L`

## 🔧 开发说明

### 文件结构
```
vscode-json-compressor/
├── package.json      # 插件配置
├── extension.js      # 主程序文件
└── README.md         # 使用说明
```

### 打包为VSIX
```bash
npm install -g vsce
vsce package
```

## 📝 注意事项

- 确保选中的文本是有效的JSON格式
- 插件会自动处理注释（// 和 /* */）
- 压缩后的JSON会保持数据完整性
- 支持嵌套的JSON对象压缩

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个插件！