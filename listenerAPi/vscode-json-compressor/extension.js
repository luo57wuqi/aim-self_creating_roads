const vscode = require('vscode');

/**
 * 激活插件
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('文本格式化插件已激活');

    // 存储原始文本用于反向操作
    let originalTexts = new Map();

    let disposable = vscode.commands.registerCommand('text-formatter.format', function () {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('请先打开一个编辑器');
            return;
        }

        const document = editor.document;
        const selection = editor.selection;
        
        // 获取选中的文本，如果没有选中则获取整个文档
        let text = '';
        let range;
        if (selection.isEmpty) {
            text = document.getText();
            range = new vscode.Range(
                document.positionAt(0),
                document.positionAt(document.getText().length)
            );
        } else {
            text = document.getText(selection);
            range = selection;
        }

        // 生成唯一标识符
        const docId = document.uri.toString();
        const rangeId = `${range.start.line}-${range.start.character}-${range.end.line}-${range.end.character}`;
        const key = `${docId}_${rangeId}`;

        try {
            let formatted;
            let message;

            // 检查是否是反向操作
            if (originalTexts.has(key)) {
                // 反向操作：恢复原始文本
                formatted = originalTexts.get(key);
                originalTexts.delete(key);
                message = '文本已恢复原始格式！';
            } else {
                // 正向操作：替换空格和换行
                originalTexts.set(key, text);
                formatted = formatText(text);
                message = '文本格式化完成！';
            }

            // 替换文本
            editor.edit(editBuilder => {
                editBuilder.replace(range, formatted);
            });

            vscode.window.showInformationMessage(message);
        } catch (error) {
            vscode.window.showErrorMessage(`格式化失败: ${error.message}`);
        }
    });

    context.subscriptions.push(disposable);
}

/**
 * 格式化文本：将空格和换行符替换为单个空格
 * @param {string} text
 * @returns {string}
 */
function formatText(text) {
    // 将多个空格、制表符、换行符等替换为单个空格
    return text
        .replace(/\s+/g, ' ')  // 将所有空白字符（空格、制表符、换行符等）替换为单个空格
        .trim();               // 移除开头和结尾的空格
}

/**
 * 停用插件
 */
function deactivate() {
    console.log('文本格式化插件已停用');
}

module.exports = {
    activate,
    deactivate
};