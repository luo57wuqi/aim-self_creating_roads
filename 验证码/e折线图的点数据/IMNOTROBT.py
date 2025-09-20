import cv2 
import numpy as np 
import matplotlib.pyplot as plt 
from ipywidgets import interact, IntSlider 
import os


def find_best_rotation(image_path, inner_radius, outer_radius, angle_step=1): 
    """ 
    修复版自动角度匹配（解决极坐标尺寸不一致问题） 
    """ 
    # 读取图像 
    img = cv2.imread(image_path) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    h, w = gray.shape 
    center = (w//2, h//2) 

    # 1. 统一极坐标高度（取外圆半径作为基准） 
    polar_height = outer_radius   

    # 2. 提取环形区域并转换极坐标（固定高度） 
    def get_polar(img, radius): 
        return cv2.warpPolar( 
            img, (360, polar_height),  # 统一高度 
            center, radius, 
            cv2.WARP_POLAR_LINEAR + cv2.WARP_INVERSE_MAP 
        ) 

    # 创建环形掩码（宽度10像素） 
    def create_ring_mask(radius): 
        mask = np.zeros_like(gray) 
        cv2.circle(mask, center, radius, 255, 10) 
        return mask 

    inner_polar = get_polar(cv2.bitwise_and(gray, gray, mask=create_ring_mask(inner_radius)), inner_radius) 
    outer_polar = get_polar(cv2.bitwise_and(gray, gray, mask=create_ring_mask(outer_radius)), outer_radius) 

    # 3. 搜索最佳角度 
    best_score = -1 
    best_angle = 0 
    all_scores = [] # 存储所有角度的匹配度

    for angle in np.arange(0, 360, angle_step): 
        # 旋转内圆极坐标图像（通过平移实现） 
        rotated = np.roll(inner_polar, int(angle), axis=1) 

        # 计算相似度（归一化互相关） 
        score = cv2.matchTemplate(rotated, outer_polar, cv2.TM_CCOEFF_NORMED)[0][0] 
        all_scores.append(score)

        if score > best_score: 
            best_score = score 
            best_angle = angle 

    # 4. 生成结果图像 
    mask = np.zeros_like(gray) 
    cv2.circle(mask, center, inner_radius, 255, -1) 
    M = cv2.getRotationMatrix2D(center, best_angle, 1) 
    rotated_inner = cv2.warpAffine(cv2.bitwise_and(img, img, mask=mask), M, (w, h)) 
    result = img.copy() 
    result[mask > 0] = rotated_inner[mask > 0] 

    # 5. 可视化 
    plt.figure(figsize=(15, 6)) 

    plt.subplot(231) 
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) 
    plt.title("原始图像") 

    plt.subplot(232) 
    plt.imshow(np.hstack([inner_polar, outer_polar]), cmap='gray')  # 现在可以拼接 
    plt.title("极坐标展开（左:内圆 | 右:外圆）") 

    plt.subplot(233) 
    plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)) 
    plt.title(f"最佳匹配（旋转{best_angle:.1f}°）") 

    # 显示匹配度曲线 
    angles = np.arange(0, 360, angle_step) 
    plt.subplot(234) 
    plt.plot(angles, all_scores) 
    plt.axvline(x=best_angle, color='r', linestyle='--') 
    plt.xlabel("旋转角度（°）") 
    plt.ylabel("匹配度") 
    plt.title("角度-匹配度曲线") 
    plt.savefig("alignment_score_curve.png")
    plt.close()

    plt.tight_layout() 
    cv2.imwrite("aligned_result.jpg", result) 
    return best_angle, result, best_score 


def extract_inner_outer_circle(image_path, inner_diameter, outer_diameter): 
    """ 
    分割正方向图片中的内圆和外圆 
    """ 
    # 读取图像 
    img = cv2.imread(image_path) 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    h, w = gray.shape 
    center = (w//2, h//2) 

    # 计算半径 
    inner_radius = inner_diameter // 2 
    outer_radius = outer_diameter // 2 

    # 创建内圆和外圆掩码 
    inner_mask = np.zeros_like(gray) 
    outer_mask = np.zeros_like(gray) 

    cv2.circle(inner_mask, center, inner_radius, 255, -1) 
    cv2.circle(outer_mask, center, outer_radius, 255, -1) 
    cv2.circle(outer_mask, center, inner_radius, 0, -1)  # 去掉内圆部分 

    # 提取内圆和外圆区域 
    inner_circle = cv2.bitwise_and(img, img, mask=inner_mask) 
    outer_circle = cv2.bitwise_and(img, img, mask=outer_mask) 

    # 保存结果 
    cv2.imwrite("inner_circle.png", inner_circle) 
    cv2.imwrite("outer_ring.png", outer_circle) 

    # 可视化结果 
    plt.figure(figsize=(12, 6)) 

    plt.subplot(121) 
    plt.imshow(cv2.cvtColor(inner_circle, cv2.COLOR_BGR2RGB)) 
    plt.title("内圆区域") 

    plt.subplot(122) 
    plt.imshow(cv2.cvtColor(outer_circle, cv2.COLOR_BGR2RGB)) 
    plt.title("外圆区域") 

    plt.tight_layout() 
    plt.show() 

# # 交互式界面 
# @interact( 
#     inner_d=IntSlider(min=50, max=200, value=104, description='内圆直径'), 
#     outer_d=IntSlider(min=150, max=300, value=297, description='外圆直径') 
# ) 
# def run_extraction(inner_d, outer_d): 
#     if inner_d >= outer_d: 
#         print("错误：内圆直径必须小于外圆直径") 
#         return 
#     extract_inner_outer_circle("imgs/demo_i.png", inner_d, outer_d)

# 读取图片中内外圆圆周上360°的像素点
def get_circle_pixels(image_path, inner_diameter, outer_diameter, num_points=360):
    """
    读取图片中内外圆圆周上360°的像素点
    
    参数:
        image_path: 图片路径
        inner_diameter: 内圆直径
        outer_diameter: 外圆直径
        num_points: 采样点数（默认360，对应360°）
    
    返回:
        inner_pixels: 内圆圆周像素列表，形状为 (num_points, 3) - BGR格式
        outer_pixels: 外圆圆周像素列表，形状为 (num_points, 3) - BGR格式
    """
    # 读取图像
    img = cv2.imread(image_path,)  # 灰度图
    if img is None:
        raise ValueError(f"无法读取图像: {image_path}")
    
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    
    # 计算半径
    inner_radius = inner_diameter // 2
    outer_radius = outer_diameter // 2
    
    # 生成角度数组
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    
    # 初始化像素数组
    inner_pixels = []
    outer_pixels = []
    
    # 采样内外圆圆周像素
    for angle in angles:
        # 计算坐标
        x_inner = int(center[0] + inner_radius * np.cos(angle))
        y_inner = int(center[1] + inner_radius * np.sin(angle))
        
        x_outer = int(center[0] + outer_radius * np.cos(angle))
        y_outer = int(center[1] + outer_radius * np.sin(angle))
        
        # 确保坐标在图像范围内
        if 0 <= x_inner < w and 0 <= y_inner < h:
            inner_pixels.append(img[y_inner, x_inner])
        else:
            inner_pixels.append(0)  # 超出范围用0填充
            
        if 0 <= x_outer < w and 0 <= y_outer < h:
            outer_pixels.append(img[y_outer, x_outer])
        else:
            outer_pixels.append(0)  # 灰度图超出范围用0填充
            
    return np.array(inner_pixels), np.array(outer_pixels)

# 绘制灰度图折线
def plot_grayscale_line_chart(inner_pixels, outer_pixels, title="灰度像素值折线图"):
    """
    绘制内外圆圆周灰度像素值的折线图。
    
    参数:
        inner_pixels: 内圆圆周像素列表 (灰度值)
        outer_pixels: 外圆圆周像素列表 (灰度值)
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    plt.plot(inner_pixels, label='inner circle')
    plt.plot(outer_pixels, label='outer circle')
    plt.title(title)
    plt.xlabel('angle degree/ sampling point')
    plt.ylabel('gray value')
    plt.legend()
    plt.grid(True)
    plt.show()


# 示例用法 (假设存在 demo_c.png 文件):
if __name__ == '__main__':
    image_path = "a.png"
    inner_d = 261
    outer_d = 297

    try:
        # 1. 提取内外圆圆周像素 (用于绘图，find_best_rotation内部会重新处理图像)
        inner_px, outer_px = get_circle_pixels(image_path, inner_d, outer_d)
        print(f"内圆像素点数量: {len(inner_px)}")
        print(f"外圆像素点数量: {len(outer_px)}")

        # 2. 绘制灰度像素值折线图
        plot_grayscale_line_chart(inner_px, outer_px, title="原始灰度像素值折线图")
        plt.savefig("grayscale_line_chart_original.png")
        plt.close()

        # 3. 寻找最佳旋转角度并计算对齐程度
        best_angle, aligned_image, alignment_score = find_best_rotation(image_path, inner_d // 2, outer_d // 2)
        print(f"最佳对齐角度: {best_angle:.2f}°")
        print(f"曲线对齐程度 (归一化互相关分数): {alignment_score:.4f}")

        # 4. 绘制对齐后的图像和匹配度曲线
        # find_best_rotation 内部已经保存了 aligned_result.jpg 和绘制了匹配度曲线
        # 这里可以再次调用 plot_grayscale_line_chart 来显示对齐后的像素曲线，如果需要的话
        # 为了避免重复计算，我们假设 find_best_rotation 已经处理了可视化部分

    except ValueError as e:
        print(e)

    # 1 分割正方向的内外圆
    # extract_inner_outer_circle("imgs/demo_i.png", 260, 290)

    # 2 读取图片中内外圆圆周上360°的像素点
    # inner_pixels, outer_pixels = get_circle_pixels("a.png", 261, 290,3600)
    # plot_grayscale_line_chart(inner_pixels, outer_pixels)  
    # inner_pixels, outer_pixels = get_circle_pixels("b.png", 261, 290,3600)
    # plot_grayscale_line_chart(inner_pixels, outer_pixels)  
    # inner_pixels, outer_pixels = get_circle_pixels("c.png", 261, 290,3600)
    # plot_grayscale_line_chart(inner_pixels, outer_pixels)
