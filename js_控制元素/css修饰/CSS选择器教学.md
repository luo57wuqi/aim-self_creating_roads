# CSS选择器详解

在CSS中，选择器是用来选择要添加样式的HTML元素的模式。通过不同类型的选择器，我们可以精确地控制网页中的元素样式。以下是常见的CSS选择器类型及其特点和作用。

## 1. 基本选择器

### 通用选择器 (*)

**语法：** `*`

**作用：** 选择所有元素。

**示例：**
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```

**特点：**
- 影响页面上的所有元素
- 通常用于重置默认样式
- 性能消耗较大，应谨慎使用

### 元素选择器

**语法：** `elementname`

**作用：** 选择指定的HTML标签。

**示例：**
```css
body {
    background-color: #f0f8f1;
}

li {
    display: block;
}
```

**特点：**
- 直接选择HTML标签
- 会影响页面上所有该类型的标签
- 优先级较低

### 类选择器

**语法：** `.classname`

**作用：** 选择所有具有指定class属性的元素。

**示例：**
```css
.fruit-card {
    border-radius: 10px;
    overflow: hidden;
}

.tomato {
    background-color: #ffcdd2;
}
```

**特点：**
- 可以应用于多个元素
- 一个元素可以有多个类
- 比元素选择器优先级高
- 命名应具有描述性

### ID选择器

**语法：** `#idname`

**作用：** 选择具有指定id属性的元素。

**示例：**
```css
#menu {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
}
```

**特点：**
- ID在页面中应该是唯一的
- 优先级高于类选择器
- 不建议过度使用，因为降低了样式的可重用性

## 2. 组合选择器

### 后代选择器

**语法：** `selector1 selector2`

**作用：** 选择selector1内部的所有selector2元素，不管嵌套多深。

**示例：**
```css
header h1 {
    font-size: 28px;
}

.fruit-card img {
    width: 100%;
    height: 120px;
}
```

**特点：**
- 可以精确定位嵌套元素
- 不要求是直接子元素
- 嵌套层级越多，性能影响越大

### 子元素选择器

**语法：** `selector1 > selector2`

**作用：** 选择selector1的直接子元素selector2。

**示例：**
```css
.fruits-list > li {
    margin-bottom: 10px;
}
```

**特点：**
- 只选择直接子元素，不包括更深层次的后代
- 比后代选择器更精确

### 相邻兄弟选择器

**语法：** `selector1 + selector2`

**作用：** 选择紧接在selector1后面的selector2元素。

**示例：**
```css
h1 + p {
    margin-top: 10px;
}
```

**特点：**
- 只选择紧邻的下一个兄弟元素
- 两个元素必须有相同的父元素

### 通用兄弟选择器

**语法：** `selector1 ~ selector2`

**作用：** 选择selector1后面的所有selector2元素。

**示例：**
```css
h1 ~ p {
    color: gray;
}
```

**特点：**
- 选择同一父元素下，指定元素之后的所有匹配元素
- 不要求是紧邻的元素

## 3. 群组选择器

**语法：** `selector1, selector2, ...`

**作用：** 同时选择多个选择器匹配的所有元素。

**示例：**
```css
th, td {
    padding: 10px;
    text-align: left;
}

.new-order, .save-order, .clear-items, .checkout {
    background-color: #1a936f;
}
```

**特点：**
- 可以减少代码重复
- 对多个不同元素应用相同样式
- 逗号分隔多个选择器

## 4. 伪类选择器

**语法：** `selector:pseudo-class`

**作用：** 选择处于特定状态的元素。

**示例：**
```css
.fruit-card:hover {
    transform: translateY(-5px);
}

.btn:hover {
    opacity: 0.9;
}
```

**常见伪类：**
- `:hover` - 鼠标悬停在元素上时
- `:active` - 元素被激活（如按钮被点击）时
- `:focus` - 元素获得焦点时
- `:first-child` - 作为父元素的第一个子元素
- `:last-child` - 作为父元素的最后一个子元素
- `:nth-child(n)` - 作为父元素的第n个子元素

**特点：**
- 可以根据元素的状态或位置应用样式
- 增强用户交互体验
- 减少JavaScript的使用需求

## 5. 伪元素选择器

**语法：** `selector::pseudo-element`

**作用：** 选择元素的特定部分或创建不存在于DOM中的元素。

**示例：**
```css
.fruit-card::before {
    content: "";
    display: block;
    height: 5px;
    background-color: #1a936f;
}

p::first-letter {
    font-size: 150%;
    font-weight: bold;
}
```

**常见伪元素：**
- `::before` - 在元素内容前插入内容
- `::after` - 在元素内容后插入内容
- `::first-letter` - 选择元素文本的第一个字母
- `::first-line` - 选择元素文本的第一行
- `::selection` - 选择用户选中的文本部分

**特点：**
- 可以创建不需要额外HTML标签的视觉效果
- 常用于添加装饰性内容
- 使用双冒号(::)语法，但单冒号(:)在大多数浏览器中也能工作

## 6. 属性选择器

**语法：** `[attribute]`, `[attribute=value]`, `[attribute^=value]`, `[attribute$=value]`, `[attribute*=value]`

**作用：** 基于元素的属性或属性值选择元素。

**示例：**
```css
[type="text"] {
    border: 1px solid #ccc;
}

[href^="https"] {
    color: green;
}

[class*="fruit"] {
    margin: 5px;
}
```

**特点：**
- 可以根据元素的属性选择元素
- 支持精确匹配、前缀匹配、后缀匹配和包含匹配
- 增强了选择的灵活性

## 7. 选择器优先级

当多个选择器应用于同一元素时，CSS使用以下规则确定哪个样式生效：

1. **!important** - 最高优先级，覆盖所有其他样式
2. **内联样式** - 直接在HTML元素上使用style属性
3. **ID选择器** - 如 #menu
4. **类选择器、属性选择器、伪类选择器** - 如 .fruit-card, [type="text"], :hover
5. **元素选择器、伪元素选择器** - 如 div, ::before
6. **通用选择器** - *

**示例：**
```css
/* 优先级: 0-0-1-0 */
div {
    color: blue;
}

/* 优先级: 0-0-1-1 */
div.fruit-card {
    color: red;
}

/* 优先级: 0-1-0-0 */
#menu {
    color: green;
}

/* 优先级: 0-1-1-1 */
#menu .fruit-card p {
    color: purple;
}

/* 覆盖所有其他样式 */
.important-text {
    color: orange !important;
}
```

## 8. 在我们的水果购物页面中的应用

在我们的水果购物页面中，我们使用了多种选择器来实现不同的样式效果：

1. **通用选择器(*)** - 重置所有元素的默认样式
2. **元素选择器(body, header, li等)** - 设置基本HTML元素的样式
3. **ID选择器(#menu)** - 设置特定元素的样式
4. **类选择器(.fruit-card, .tomato等)** - 设置具有特定类的元素样式
5. **后代选择器(.fruit-card img, header h1等)** - 设置嵌套元素的样式
6. **伪类选择器(.fruit-card:hover, .btn:hover)** - 添加交互效果
7. **群组选择器(th, td)** - 同时设置多个元素的相同样式

通过合理使用这些选择器，我们可以创建出结构清晰、样式丰富的网页，同时保持CSS代码的可维护性和可重用性。

## 9. 小练习

尝试以下练习来加深对CSS选择器的理解：

1. **修改所有水果卡片的边框**：
   ```css
   .fruit-card {
       border: 2px solid #1a936f;
   }
   ```

2. **为列表项添加悬停效果**：
   ```css
   li:hover .fruit-card {
       transform: scale(1.05);
   }
   ```

3. **使用属性选择器选择特定图片**：
   ```css
   img[alt="番茄"] {
       border: 3px solid red;
   }
   ```

4. **使用伪元素为价格添加货币符号**：
   ```css
   .fruit-price::before {
       content: "价格: ";
       font-weight: normal;
       color: #666;
   }
   ```

5. **使用子元素选择器设置列表样式**：
   ```css
   .fruits-list > li:nth-child(odd) {
       background-color: rgba(0, 0, 0, 0.05);
   }
   ```

通过这些练习，你可以更好地理解和掌握CSS选择器的使用方法和特点。