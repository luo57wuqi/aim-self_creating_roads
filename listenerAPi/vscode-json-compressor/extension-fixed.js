const vscode = require('vscode');

/**
 * 激活插件
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('JSON Compressor 插件已激活');

    let disposable = vscode.commands.registerCommand('json-compressor.compress', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('请先打开一个编辑器');
            return;
        }

        const document = editor.document;
        const selection = editor.selection;
        
        // 获取选中的文本，如果没有选中则获取整个文档
        let text = '';
        if (selection.isEmpty) {
            text = document.getText();
        } else {
            text = document.getText(selection);
        }

        try {
            // 压缩JSON
            const compressed = compressAnyJson(text);
            
            // 替换选中的文本或整个文档
            editor.edit(editBuilder => {
                if (selection.isEmpty) {
                    const fullRange = new vscode.Range(
                        document.positionAt(0),
                        document.positionAt(document.getText().length)
                    );
                    editBuilder.replace(fullRange, compressed);
                } else {
                    editBuilder.replace(selection, compressed);
                }
            });

            vscode.window.showInformationMessage('JSON 压缩完成！');
        } catch (error) {
            vscode.window.showErrorMessage(`压缩失败: ${error.message}`);
        }
    });

    context.subscriptions.push(disposable);
}

/**
 * 智能压缩任何JSON/JS对象格式
 * @param {string} text
 * @returns {string}
 */
function compressAnyJson(text) {
    // 移除注释
    text = text.replace(/\/\*[\s\S]*?\*\//g, '');
    text = text.replace(/\/\/.*$/gm, '');

    // 尝试直接解析
    let obj;
    try {
        obj = JSON.parse(text);
    } catch (parseError) {
        // 处理各种格式问题
        let jsText = text.trim();
        
        // 提取对象或数组部分
        const objectMatch = jsText.match(/\{[\s\S]*\}/);
        const arrayMatch = jsText.match(/\[[\s\S]*\]/);
        let targetMatch = objectMatch || arrayMatch;
        
        if (!targetMatch) {
            throw new Error('未找到有效的数据');
        }
        
        jsText = targetMatch[0];
        
        // 修复各种格式问题
        jsText = fixJsonFormat(jsText);
        
        try {
            obj = JSON.parse(jsText);
        } catch (e) {
            // 最后尝试eval
            try {
                const func = new Function('return ' + jsText);
                obj = func();
            } catch (evalError) {
                throw new Error('无法解析格式：' + e.message);
            }
        }
    }

    // 压缩为单行
    return JSON.stringify(obj);
}

/**
 * 修复JSON格式问题
 * @param {string} text
 * @returns {string}
 */
function fixJsonFormat(text) {
    // 修复中文引号
    text = text.replace(/[""]/g, '"');
    
    // 修复单引号
    text = text.replace(/'/g, '"');
    
    // 处理数组中的对象语法
    if (text.startsWith('[') && text.includes(':') && !text.includes('{')) {
        // 将数组中的键值对转换为对象
        text = text.replace(/\[\s*([^\]]+)\s*\]/, function(match, content) {
            // 清理内容并转换为对象格式
            content = content.replace(/\s*:\s*/g, '":"');
            content = content.replace(/,\s*$/g, ''); // 移除末尾逗号
            return '{' + content + '}';
        });
    }
    
    // 修复键值对格式
    text = text.replace(/(["\w]+)\s*:\s*([^,\]}]+)/g, '"$1":$2');
    
    // 修复数字格式
    text = text.replace(/:\s*([\d.]+)(?=[,}\]])/g, ':$1');
    
    // 修复布尔值
    text = text.replace(/:\s*(true|false)(?=[,}\]])/g, ':$1');
    
    // 修复字符串值
    text = text.replace(/:\s*([^",\]}]+)(?=[,}\]])/g, ':"$1"');
    
    // 移除所有尾随逗号
    text = text.replace(/,(\s*[}\]])/g, '$1');
    
    return text;
}

/**
 * 停用插件
 */
function deactivate() {
    console.log('JSON Compressor 插件已停用');
}

module.exports = {
    activate,
    deactivate
};