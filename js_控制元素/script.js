// 一、webapi 控制元素 2025-09-11 16:27:33
//  js语法介绍 https://developer.mozilla.org/docs/Web/API/Window/open 2025-09-11 17:59:57
// console.log('hello world')
// document.title="换网页标题，浏览器最上方的文本"
// console.log(document.body)
// document.body.innerHTML = "大家好,我是RPA/n这里是修改doby的innerHtml内容就到了我"

// 1.1 css选择器
//返回符合条件的元素
document.querySelector(`button`) 
// 获取内部文本
let btn = document.querySelector(`button`)
btn.innerHTML //返回符合条件的元素的内部文本
btn.getAttribute('id') //返回符合条件的元素的属性值
debugger //设置断点
console.log(btn.id)
// 设置属性值
btn.setAttribute('id','newId')
console.log(btn['id'])



// 移除属性
// btn.removeAttribute('id')

// 应用：
    // 获取浏览器的图片，文字等数据 eg
    //  item.jd.com/100008341027.html
    //  document.querySelector("#spec-img").src
    // 'https://img12.360buyimg.com/n1/s720x720_jfs/t1/340670/28/3463/109944/68b15ebbFacf5a74f/c8dd91a0dabd1e3d.jpg.avif'

    // 1  style 样式 get datas
    let ele =  document.querySelector("#css_inner_url")
    let getComputerStyles = window.getComputedStyle(ele)
    let bgImage = getComputerStyles.backgroundImage
    console.log(bgImage) 
    // 'url("file:///C:/Users/admin/Desktop/RPA/skills/js_%E6%8E%A7%E5%88%B6%E5%85%83%E7%B4%A0/src/atrributImag.jpg.avif")'
    // 提取图片url
    let imgUrl = bgImage.match(/url\("(.*)"\)/)[1]
    console.log(imgUrl)
    // 'file:///C:/Users/admin/Desktop/RPA/skills/js_%E6%8E%A7%E5%88%B6%E5%85%83%E7%B4%A0/src/atrributImag.jpg.avif'
    // 获取属性直
    let image = getComputerStyles.getPropertyValue('background-image')
    // 2 content
        let eleCon =  document.querySelector(".my-paragraph")
        let getComputerStylesCont = window.getComputedStyle(eleCon,"::before")
        // getComputedStyle 可以获取元素的所有计算样式，包括继承的样式；
        // 样式数据存储在window对象的computedStyle（）
        // getComputedStyle方法用于获取元素的计算样式
            // 参数1: elt - 要获取样式的元素
            // 参数2: pseudoElt - 可选的伪元素字符串(如 '::before'、'::after')
            // 返回值: 返回一个实时的 CSSStyleDeclaration 对象,包含元素的所有计算样式
        let styleContent = getComputerStylesCont.content
        console.log(styleContent) 
        // '" 样式保存的文本数据! "'
// 3 js delete 元素的属性
     let input = document.querySelector(".only_js_remove input")
     console.log(input)
     debugger
     input.removeAttribute('readonly')

 // 4 事件监听
    let btnA =document.querySelector(`button`)
    btnA.addEventListener('click',()=>{alert(`A!,I hit by your mouse`)})
// 5 get childs || parent elements
    let childs = document.querySelector('div').children
    let parent = document.querySelector('div').parentElement
    console.log(childs)
    console.log(parent)
window.open()

//

// 5  debugger //设置断点

// 6 browser api
    // window.console.log('hello,everyone!')
    // window.innerHeight
    // window.location.href
    // window.open(`https:\\www.baidu.com`)
    // window.history
    // 存储数据 localStorage :
    // localStorage.setItem('userInfo', JSON.stringify({ name: '张三', age: 18 }))

// 二、webapi 控制窗口
    // console.log(window.document.getElementById('9527'))
    // window对象是JavaScript中的全局对象，它代表浏览器窗口
    // window对象包含了许多重要属性和方法：
    // - document: 用于访问和操作网页内容
    // - location: 提供当前URL信息和导航功能
    // - history: 管理浏览历史
    // - localStorage: 提供本地存储功能
    // - console: 用于调试和日志输出
    // - setTimeout/setInterval: 用于定时执行代码
    // 所有全局变量和函数都是window对象的属性


    // window.document.getElementById('9527').innerHTML = '我是修改后的按钮1'
    // // 1 打开新网页
    // window.openURL = 'https://www.baidu.com'
    // // 2 打开新网页 另一个标签页
    // // window.open(window.openURL,'_blank')
    // // 3 打开新网页 本标签页
    // // window.open(window.openURL,'_self')
    // // 4 打开新网页 新窗口
    // // window.open(window.openURL,'_new')
    // // 5 打开新网页 新窗口 并返回窗口对象
    // // const newWindow = window.open(window.openURL,'_new')

    // // 6 关闭新窗口
    // newWindow.close()


//  js 打开新网页
    // // 1 替换当前网页
    // window.location.href = window.openURL
    // 2 存储数据 localStorage :
    // localStorage.setItem('userInfo', JSON.stringify({ name: '张三', age: 18 }))
    // 3 BroadcastChannel（同源页面广播） const channel = new BroadcastChannel('myChannel')
    // 4   IndexedDB存储（大数据量）
    // 打开数据库 const request = indexedDB.open('MyDatabase', 1)

