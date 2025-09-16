// 压缩版数据
const sourceDatas = {"268_BSL00218精选":35,"268_BSL00218想要":3000,"269_BLJ05036已买":56,"269_BLJ05036精选":23,"269_BLJ05036想要":296,"270_BLJ02798已买":34,"270_BLJ02798精选":13,"270_BLJ02798想要":266};

// 转换数据为二维数组
const temp = {};
for (const [key, value] of Object.entries(sourceDatas)) {
    const match = key.match(/^(\d+)_([^_]+)(已买|精选|想要)$/);
    if (match) {
        const index = match[1];
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

// 转换为CSV字符串
const headers = ["货号","已买","精选","想要"];
const csvString = [headers.join(","),...result.map(row => row.join(","))].join("\n");

// 下载函数
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

// 执行下载
downloadCSV(csvString, "产品数据.csv");