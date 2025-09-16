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
            const compressed = compressJson(text);
            
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
    // 首先尝试自动修复格式
    text = autoFixJsonFormat(text);
    
    // 尝试直接解析
    let obj;
    try {
        obj = JSON.parse(text);
    } catch (parseError) {
        // 如果解析失败，尝试提取有效部分
        let jsText = text.trim();
        
        // 提取对象或数组部分
        const objectMatch = jsText.match(/\{[\s\S]*\}/);
        const arrayMatch = jsText.match(/\[[\s\S]*\]/);
        let targetMatch = objectMatch || arrayMatch;
        
        if (!targetMatch) {
            throw new Error('未找到有效的数据');
        }
        
        jsText = targetMatch[0];
        
        // 再次尝试修复
        jsText = autoFixJsonFormat(jsText);
        
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
 * 停用插件
 */
function deactivate() {
    console.log('JSON Compressor 插件已停用');
}

module.exports = {
    activate,
    deactivate
};