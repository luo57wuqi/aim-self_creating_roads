sourceDatas = [
    "268_BSL00218精选": 35,
    "268_BSL00218想要": 3000,
    "269_BLJ05036已买": 56,
    "269_BLJ05036精选": 23,
    "269_BLJ05036想要": 296,
    "270_BLJ02798已买": 34,
    "270_BLJ02798精选": 13,
    "270_BLJ02798想要": 266
};



// 1. 转换数据为二维数组
const temp = {};
for (const [key, value] of Object.entries(sourceDatas)) {
    // 循环字典for (const [key,value] of Object.entries(sourceDatas)) {} 
    //  关键词 for ()声明循环的变量，一个多个数据的变量，或则循环对象，和每次循环递增
    const match = key.match(/^(\d+)_([^_]+)(已买|精选|想要)$/);
    // 字符串的match函数，获取数字_商品编码_已买|精选|想要这样的规则的符号；/^字符开始，()保留的内容，（A|B|C）|满足就匹配 $字符结束/
    // 正则表达式解释: /^(\d+)_([^_]+)(已买|精选|想要)$/
    // ^                    - 匹配字符串的开始
    // (\d+)                - 第一个捕获组,匹配一个或多个数字
    // _                    - 匹配下划线字符
    // ([^_]+)              - 第二个捕获组,匹配一个或多个非下划线字符
    // [^xx]               - 匹配除了xx以外的任意字符
    // (已买|精选|想要)      - 第三个捕获组,匹配这三个固定文本之一
    // $ - 匹配字符串的结束

    if (match) {
        // 
        const index = match[1];
        // 赋值序号为批判的第一个()的内容
        const productCode = match[2];
        const type = match[3];
        
        if (!temp[index]) {
            temp[index] = [productCode, 0, 0, 0];
        }
        
        if (type === "已买") temp[index][1] = value;
        else if (type === "精选") temp[index][2] = value;
        else if (type === "想要") temp[index][3] = value;
    }
}

const result = Object.values(temp);

// 2. 转换为CSV字符串
const headers = ["货号", "已买", "精选", "想要"];
const csvRows = [
    headers.join(","), // 添加表头
    ...result.map(row => row.join(",")) // 添加数据行
];
const csvString = csvRows.join("\n");

// 3. 创建下载链接
function downloadCSV(csvString, filename) {
    const blob = new Blob(["\uFEFF" + csvString], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = "hidden";
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 4. 调用下载函数
downloadCSV(csvString, "产品数据.csv");