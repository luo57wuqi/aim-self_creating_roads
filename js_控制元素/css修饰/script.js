// // 水果购物页面的JavaScript交互功能

// 暂时不用
// document.addEventListener('DOMContentLoaded', function() {
//     // 获取所有水果卡片元素
//     const fruitCards = document.querySelectorAll('.fruit-card');
//     // 获取订单表格的tbody
//     const orderTableBody = document.querySelector('.order-summary tbody');
//     // 获取合计金额元素
//     const totalPriceElement = document.querySelector('.total-price');
//     // 获取按钮元素
//     const newOrderBtn = document.querySelector('.new-order');
//     const saveOrderBtn = document.querySelector('.save-order');
//     const clearItemsBtn = document.querySelector('.clear-items');
//     const checkoutBtn = document.querySelector('.checkout');
//     // 获取所有列表项
//     const fruitItems = document.querySelectorAll('.fruits-list li');
    
//     // 订单数据
//     let orderItems = [];
//     let totalPrice = 0;
    
//     // 为每个水果卡片添加点击事件
//     fruitCards.forEach(card => {
//         card.addEventListener('click', function() {
//             // 获取水果信息
//             const fruitName = this.querySelector('.fruit-name').textContent;
//             const fruitPriceText = this.querySelector('.fruit-price').textContent;
//             const fruitPrice = parseInt(fruitPriceText.replace('¥', '').trim());
            
//             // 检查订单中是否已有该水果
//             const existingItem = orderItems.find(item => item.name === fruitName);
            
//             if (existingItem) {
//                 // 如果已存在，增加数量
//                 existingItem.quantity += 1;
//                 existingItem.subtotal = existingItem.quantity * existingItem.price;
//             } else {
//                 // 如果不存在，添加新项目
//                 orderItems.push({
//                     name: fruitName,
//                     price: fruitPrice,
//                     quantity: 1,
//                     subtotal: fruitPrice
//                 });
//             }
            
//             // 添加点击效果
//             this.classList.add('clicked');
//             setTimeout(() => {
//                 this.classList.remove('clicked');
//             }, 200);
            
//             // 更新订单显示
//             updateOrderDisplay();
//         });
//     });
    
//     // 新建订单按钮点击事件
//     newOrderBtn.addEventListener('click', function() {
//         orderItems = [];
//         totalPrice = 0;
//         updateOrderDisplay();
//     });
    
//     // 保存订单按钮点击事件
//     saveOrderBtn.addEventListener('click', function() {
//         if (orderItems.length > 0) {
//             alert('订单已保存！');
//         } else {
//             alert('订单为空，无法保存！');
//         }
//     });
    
//     // 删除商品按钮点击事件
//     clearItemsBtn.addEventListener('click', function() {
//         if (orderItems.length > 0) {
//             if (confirm('确定要删除所有商品吗？')) {
//                 orderItems = [];
//                 totalPrice = 0;
//                 updateOrderDisplay();
//             }
//         } else {
//             alert('订单为空，没有商品可删除！');
//         }
//     });
    
//     // 确认订单按钮点击事件
//     checkoutBtn.addEventListener('click', function() {
//         if (orderItems.length > 0) {
//             alert(`订单已确认，总金额：¥ ${totalPrice}`);
//             orderItems = [];
//             totalPrice = 0;
//             updateOrderDisplay();
//         } else {
//             alert('订单为空，请先添加商品！');
//         }
//     });
    
//     // 更新订单显示函数
//     function updateOrderDisplay() {
//         // 清空表格
//         orderTableBody.innerHTML = '';
        
//         // 重新计算总价
//         totalPrice = 0;
        
//         // 添加订单项到表格
//         orderItems.forEach(item => {
//             const row = document.createElement('tr');
            
//             // 商品名称
//             const nameCell = document.createElement('td');
//             nameCell.textContent = item.name;
//             row.appendChild(nameCell);
            
//             // 数量
//             const quantityCell = document.createElement('td');
//             quantityCell.textContent = item.quantity;
//             row.appendChild(quantityCell);
            
//             // 价格
//             const priceCell = document.createElement('td');
//             priceCell.textContent = `¥ ${item.price}`;
//             row.appendChild(priceCell);
            
//             // 小计
//             const subtotalCell = document.createElement('td');
//             subtotalCell.textContent = `¥ ${item.subtotal}`;
//             row.appendChild(subtotalCell);
            
//             // 添加行到表格
//             orderTableBody.appendChild(row);
            
//             // 累加总价
//             totalPrice += item.subtotal;
//         });
        
//         // 更新总价显示
//         totalPriceElement.textContent = `¥ ${totalPrice}`;
//     }
// });

// 影刀调研js 本质就是不写函数名，但是（）传入要处理的参数

// 1 
let menuList = document.querySelectorAll('#menuUL >li')
// 3 每次点一次图片增加一个采购表
let selectedFoodList = [];
// 2  增加交互功能 给每个li增加一个点击事件
for (let i =0;i< menuList.length;i++){
    let listItem = menuList[i]
    listItem.addEventListener('click',function(){
        //添加功能3 
        // 修正：正确获取水果名称和价格
        let fruitCard = listItem.querySelector('.fruit-card');
        let name = fruitCard.querySelector('.fruit-name').innerHTML;
        let price = Number(fruitCard.querySelector('.fruit-price').innerHTML.match(/\d+/g)[0]);

        // 给每个item都增加一个点击事件
        // 注意：这里不需要再次添加点击事件，因为外层已经有了
        // 点击一次增加一个采购表
        if (selectedFoodList.length !=0){
            // 是否已经有商品名字了,有名字就增加对应商品的数量 
            // 如果已经没在呢？那就，加入
            let isAdd = false; //保存是否已加入的状态
            for (let i =0;i<selectedFoodList.length;i++){
                if (selectedFoodList[i].name === name){ 
                    // 商品名已经存在，又被点击，那就是增加购买数量
                    // 数量增加
                    selectedFoodList[i].count++;
                    isAdd = true;
                    break;
                }
            }
            
            if(!isAdd){ 
                // isAdd === false ===值和typeOf都一致
                // 商品名不存在，加入
                selectedFoodList.push({
                    name: name,
                    price: price,
                    count: 1
                })
            }
        }else{
            // 如果订单列表空，说明就是第一个订单，直接加入到这个订单
            // （对象来存储每个商品数量的数据）
            selectedFoodList.push({
                name: name,
                price: price,
                count: 1
            })
        }
        
        // 更新订单显示
        updateSelectNodeList();
        })
    }
// 4 把数据显示出来
function updateSelectNodeList(){
    let selected_Ul = document.querySelector('#selectedUl');
    selected_Ul.innerHTML = '';
    if(selectedFoodList.length != 0){
        let amount = 0;
        // 修正：循环应该从0开始，而不是1
        for (let i = 0; i < selectedFoodList.length; i++){
            // 5 网页新增元素  使用6
            let li = generateSelectedListItem(selectedFoodList[i])
            selected_Ul.appendChild(li)
            // 7 金额加在这里，需要一个变量存储 amount:每个商品的价格和数量总和
            amount = amount + selectedFoodList[i].price * selectedFoodList[i].count
        }
        // 8 读取合计展示价格的元素
        let total_amount = document.querySelector('#total_amount');
        total_amount.innerHTML = "￥" + amount;
    } else {
        // 9 如果变量selectedFoodList为空，合计设为0
        let total_amount = document.querySelector('#total_amount');
        total_amount.innerHTML = "￥0"
    }
    
}

// 6 创建商品订单列表
function generateSelectedListItem(item){
    let li = document.createElement('li')

    // 创建商品名称容器div
    const nameDiv = document.createElement('div');
    nameDiv.classList.add("cell", "nameCell");

    // 创建圆形图标span -- 存放商品图标
    const icoSpan = document.createElement('span');
    icoSpan.classList.add("circle");

    // 创建商品名称span 存放商品名
    const nameSpan = document.createElement('span');
    nameSpan.classList.add('name');
    nameSpan.textContent = item.name; // 设置商品名称

    // 将图标和名称添加到容器中
    nameDiv.appendChild(icoSpan);
    nameDiv.appendChild(nameSpan);

    // 创建一个div元素用于显示商品数量
    // cell类用于控制元素布局样式
    let countDiv = document.createElement('div')
    countDiv.classList.add('cell') // 添加cell类使其与其他元素保持一致的布局样式

    // 创建一个div元素用于显示商品单价
    // 参数: 无
    // 作用: 1. 创建一个新的div元素来显示商品价格
    //      2. 添加cell和amountCell类来保持布局样式一致
    //      3. cell类控制基础布局，amountCell类专门用于金额显示样式
    let priceDiv = document.createElement('div')
    priceDiv.classList.add('cell','amountCell')

    // 存放合并后的金额
    let amountDiv = document.createElement('div')
    amountDiv.classList.add('cell','amountCell')
    
    // 正确添加所有子元素
    li.appendChild(nameDiv);
    li.appendChild(countDiv);
    li.appendChild(priceDiv);
    li.appendChild(amountDiv);
    
    // 把item的数据传入
    nameSpan.innerHTML = item.name
    countDiv.innerHTML = item.count
    priceDiv.innerHTML = item.price
    amountDiv.innerHTML = `￥${item.price*item.count}`
    return li
}

// 10 按钮增加点击事件
let order_button = document.querySelector(`#order_button`)
order_button.addEventListener(`click`,function(){
    // 点击新建订单按钮，清空订单列表
    selectedFoodList = [];
    updateSelectNodeList()

})

// 14 随机水果机按钮
let randomFruitBtn = document.querySelector('#random_fruit')
randomFruitBtn.addEventListener('click',function(){
    // 获取所有水果卡片
    let fruitCards = document.querySelectorAll('.fruit-card');
    
    // 随机选择一个水果索引
    let randomIndex = Math.floor(Math.random() * fruitCards.length);
    let selectedFruit = fruitCards[randomIndex];
    
    // 获取水果信息
    let name = selectedFruit.querySelector('.fruit-name').innerHTML;
    let price = Number(selectedFruit.querySelector('.fruit-price').innerHTML.match(/\d+/g)[0]);
    
    // 添加到订单
    let existingItem = selectedFoodList.find(item => item.name === name);
    if (existingItem) {
        existingItem.count++;
    } else {
        selectedFoodList.push({
            name: name,
            price: price,
            count: 1
        });
    }
    
    // 添加动画效果
    selectedFruit.classList.add('random-selected');
    setTimeout(() => {
        selectedFruit.classList.remove('random-selected');
    }, 1000);
    
    // 更新订单显示
    updateSelectNodeList();
})

// 11 delete fruits
let delete_button = document.querySelector(`#delete_button`)
delete_button.addEventListener('click', function() {
    // 检查订单列表是否为空
    if (selectedFoodList.length === 0) {
        return; // 如果订单为空则直接返回
    }

    // 获取最后一个商品项
    let lastItem = selectedFoodList[selectedFoodList.length - 1];

    if (lastItem.count === 1) {
        // 如果最后一个商品数量为1，则从列表中移除该商品
        selectedFoodList.pop();
    } else {
        // 如果商品数量大于1，则减少数量
        lastItem.count--;
    }

    // 更新订单显示
    updateSelectNodeList();
});

// 12 保存订单
let save_button = document.querySelector(`#save_button`)
save_button.addEventListener('click',()=>{
    selectedFoodList = []
    updateSelectNodeList()
    window.alert('订单保存成功')
}) 

//13  监听提交订单按钮事件
let confirm_button = document.querySelector(`#confirm_button`)
confirm_button.addEventListener('click',()=>{
    // 显示提示信息
    window.alert('商品正在准备中')
    
    // 发送订单数据到服务器 等待响应后，给快递单号
    fetch('http://localhost:3000/order/getOrder', {
        method: 'POST', // POST
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            order: selectedFoodList
        }),
        // 设置跨域请求时是否携带cookie等身份凭证信息
        // include: 跨域请求会携带用户凭证(cookie等)
        // same-origin: 只有同源请求才会携带凭证
        // omit: 任何请求都不携带凭证
        credentials: 'include'
    })
    .then(response => {
        // 检查响应状态
        if (!response.ok) {
            throw new Error('网络请求失败');
        }
        return response.json();
    })
    .then(data => {
        // 处理响应数据
        console.log(data);
        // 显示快递单号
        window.alert(`您的快递单号为：${data.orderNumber}`)
        
        // 清空订单列表
        selectedFoodList = [];
        updateSelectNodeList();
        
        window.alert('订单提交成功');
    })
    .catch(error => {
        console.error('提交订单时发生错误:', error);
        window.alert('订单提交失败，请重试');
        // 假数据
        window.alert(`您的快递单号为：${Math.random().toString(36).substring(2, 19)}`);
        // 打印cookie
        window.alert(document.cookie)
     });
})
