import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# --------------------------
# 1. 关键参数配置（需根据 verify.jpeg 实际尺寸调整！）
# --------------------------
# 第一步：先运行代码看日志，若识别异常，按以下步骤调整参数：
# 1. 用画图软件打开 verify.jpeg，查看图片像素尺寸（如 300x300、400x400）
# 2. 测量中间小圆的半径（从圆心到小圆边缘的像素数）
# 3. 外环半径默认是图片尺寸的一半（正方形验证码通用）
img_path = "demo_j.png"  # 你的验证码图片路径
img_size = None           # 自动获取图片尺寸（无需手动填）
center = None             # 自动计算圆心（正方形图片默认中心）
inner_radius = 120        # 初始值：中间小圆半径（需根据实际调整）
outer_radius = None       # 自动计算（图片尺寸//2）
sector_count = 12         # 扇形分区（30°/个，无需改）
similarity_threshold = 0.6# 相似度阈值（可微调，0.5-0.7之间）

# 用于保存中间结果的文件夹，若不存在则创建
save_dir = "captcha_analysis"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


# --------------------------
# 2. 核心工具函数
# --------------------------
def rotate_image(img, angle, center):
    """旋转图片（适配任意圆心）"""
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))

def get_image_info(img_path):
    """读取图片并获取尺寸、圆心、外环半径"""
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"未找到图片：{img_path}，请检查路径是否正确")
    h, w = img.shape[:2]
    if h != w:
        print(f"⚠️  警告：图片不是正方形（{w}x{h}），默认按中心计算圆心")
    img_size = max(h, w)
    center = (w//2, h//2)  # 图片中心（无论是否正方形）
    outer_radius = min(w, h) // 2  # 外环半径（避免超出图片）
    return img, img_size, center, outer_radius


# --------------------------
# 3. 验证码核心分析逻辑
# --------------------------
def get_inner_circle_pixels(img, center, inner_radius):
    """提取中间小圆的像素（排除背景干扰）"""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, inner_radius, 255, -1)  # 绘制小圆掩码
    # 提取小圆像素（过滤纯黑色背景）
    inner_pixels = cv2.bitwise_and(img, img, mask=mask)
    # 保存提取的内环像素图片
    cv2.imwrite(os.path.join(save_dir, "inner_circle_pixels.png"), inner_pixels)
    return inner_pixels, mask

def get_outer_sector_pixels(img, center, outer_radius, inner_radius, angle_start, angle_end):
    """提取外环对应扇形的像素（排除中间小圆）"""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    # 绘制外环扇形
    cv2.ellipse(mask, center, (outer_radius, outer_radius), 0, angle_start, angle_end, 255, -1)
    # 减去中间小圆（只保留外环区域）
    cv2.circle(mask, center, inner_radius, 0, -1)
    # 提取扇形像素
    outer_sector = cv2.bitwise_and(img, img, mask=mask)
    # 保存提取的外环扇形像素图片，用角度区分命名
    sector_name = f"outer_sector_{int(angle_start)}_{int(angle_end)}.png"
    cv2.imwrite(os.path.join(save_dir, sector_name), outer_sector)
    return outer_sector, mask

def calculate_actual_similarity(img, center, inner_radius, outer_radius):
    """计算中间小圆与外环的对齐相似度（核心）"""
    # 提取中间小圆像素
    inner_pixels, _ = get_inner_circle_pixels(img, center, inner_radius)
    sector_sims = []
    
    # 逐个扇形对比
    for i in range(sector_count):
        start_angle = i * (360 / sector_count)
        end_angle = (i + 1) * (360 / sector_count)
        
        # 提取外环当前扇形的像素
        outer_sector, _ = get_outer_sector_pixels(img, center, outer_radius, inner_radius, start_angle, end_angle)
        
        # 模拟“旋转中间小圆”对齐：反向旋转内圆，抵消偏移
        rotated_inner = rotate_image(inner_pixels, -start_angle, center)
        # 提取旋转后内圆的对应扇形
        rotated_inner_sector, _ = get_outer_sector_pixels(rotated_inner, center, outer_radius, inner_radius, start_angle, end_angle)
        
        # 计算相似度（用模板匹配，抗半透明和颜色干扰）
        def get_valid_similarity(a, b):
            # 转为灰度图，减少颜色干扰
            a_gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
            b_gray = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
            # 过滤纯黑像素（只保留有效图案）
            a_valid = a_gray[a_gray > 10]  # 排除接近黑色的像素
            b_valid = b_gray[b_gray > 10]
            if len(a_valid) < 10 or len(b_valid) < 10:
                return 0.0  # 有效像素太少，跳过
            # 模板匹配计算相似度（-1~1，1为完全匹配）
            return cv2.matchTemplate(a_gray, b_gray, cv2.TM_CCOEFF_NORMED)[0][0]
        
        # 计算当前扇形相似度
        sim = get_valid_similarity(rotated_inner_sector, outer_sector)
        sector_sims.append(round(sim, 2))
    
    avg_sim = round(np.mean(sector_sims), 2)
    return avg_sim, sector_sims


# --------------------------
# 4. 可视化分析结果（方便调试）
# --------------------------
def visualize_result(img, center, inner_radius, outer_radius):
    """绘制分析标记：圆心、小圆、外环、扇形分区"""
    img_copy = img.copy()
    # 画圆心（红色点）
    cv2.circle(img_copy, center, 5, (0, 0, 255), -1)
    # 画中间小圆（青色虚线）
    cv2.circle(img_copy, center, inner_radius, (255, 0, 0), 2, cv2.LINE_AA)
    # 画外环（绿色虚线）
    cv2.circle(img_copy, center, outer_radius, (0, 255, 0), 2, cv2.LINE_AA)
    # 画扇形分区线（黄色实线）
    for i in range(sector_count):
        angle = i * (360 / sector_count)
        rad = np.radians(angle)
        x = int(center[0] + outer_radius * np.cos(rad))
        y = int(center[1] + outer_radius * np.sin(rad))
        cv2.line(img_copy, center, (x, y), (0, 255, 255), 1, cv2.LINE_AA)
    # 保存可视化标记后的图片
    cv2.imwrite(os.path.join(save_dir, "visualized_result.png"), img_copy)
    return img_copy


# --------------------------
# 5. 执行测试（主流程）
# --------------------------
if __name__ == "__main__":
    # 1. 读取图片并初始化参数
    img, img_size, center, outer_radius = get_image_info(img_path)
    print(f"📊 图片信息：尺寸{img.shape[1]}x{img.shape[0]}，圆心{center}，外环半径{outer_radius}，小圆半径{inner_radius}")
    
    # 2. 计算相似度
    avg_sim, sector_sims = calculate_actual_similarity(img, center, inner_radius, outer_radius)
    
    # 3. 输出结果
    print(f"\n=== verify.jpeg 测试结果 ===")
    print(f"平均相似度：{avg_sim}（阈值：{similarity_threshold}）")
    print(f"各扇形相似度：{sector_sims}")
    result = "✅ 对齐（验证通过）" if avg_sim > similarity_threshold else "❌ 未对齐（需调整旋转角度）"
    print(f"最终结论：{result}")
    
    # 4. 可视化分析（显示标记后的图片）
    visualized_img = visualize_result(img, center, inner_radius, outer_radius)
    plt.figure(figsize=(8, 8))
    plt.imshow(cv2.cvtColor(visualized_img, cv2.COLOR_BGR2RGB))
    plt.title(f"verify.jpeg 分析结果\n{result} | 平均相似度：{avg_sim}")
    plt.axis("off")
    plt.show()
    
    # 5. 调试建议
    if avg_sim < similarity_threshold:
        print(f"\n🔧 调试建议：")
        print(f"1. 若中间小圆标记偏差，调整 inner_radius（当前：{inner_radius}）")
        print(f"2. 若相似度接近阈值，可降低 similarity_threshold（当前：{similarity_threshold}）")
        print(f"3. 若扇形分区错位，检查图片是否为正方形（当前：{img.shape[1]}x{img.shape[0]}）")