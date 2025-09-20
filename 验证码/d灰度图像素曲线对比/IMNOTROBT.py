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

    for angle in np.arange(0, 360, angle_step): 
        # 旋转内圆极坐标图像（通过平移实现） 
        rotated = np.roll(inner_polar, int(angle), axis=1) 

        # 计算相似度（归一化互相关） 
        score = cv2.matchTemplate(rotated, outer_polar, cv2.TM_CCOEFF_NORMED)[0][0] 

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
    scores = [cv2.matchTemplate(np.roll(inner_polar, int(a), axis=1), 
                                outer_polar, cv2.TM_CCOEFF_NORMED)[0][0] 
             for a in angles] 

    plt.subplot(234) 
    plt.plot(angles, scores) 
    plt.axvline(x=best_angle, color='r', linestyle='--') 
    plt.xlabel("旋转角度（°）") 
    plt.ylabel("匹配度") 
    plt.title("角度-匹配度曲线") 

    plt.tight_layout() 
    cv2.imwrite("aligned_result.jpg", result) 
    return best_angle, result 


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

# 交互式界面 
@interact( 
    inner_d=IntSlider(min=50, max=200, value=104, description='内圆直径'), 
    outer_d=IntSlider(min=150, max=300, value=297, description='外圆直径') 
) 
def run_extraction(inner_d, outer_d): 
    if inner_d >= outer_d: 
        print("错误：内圆直径必须小于外圆直径") 
        return 
    extract_inner_outer_circle("imgs/demo_i.png", inner_d, outer_d)

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
    img = cv2.imread(image_path)
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
            inner_pixels.append([0, 0, 0])  # 超出范围用黑色填充
            
        if 0 <= x_outer < w and 0 <= y_outer < h:
            outer_pixels.append(img[y_outer, x_outer])
        else:
            outer_pixels.append([0, 0, 0])  # 超出范围用黑色填充
    
    return np.array(inner_pixels), np.array(outer_pixels)

# 可视化内外圆圆周像素
def visualize_circle_pixels(inner_pixels, outer_pixels):
    """
    可视化内外圆圆周像素
    """
    plt.figure(figsize=(15, 8))
    
    # 转换为RGB格式用于显示
    inner_rgb = cv2.cvtColor(inner_pixels.reshape(1, -1, 3), cv2.COLOR_BGR2RGB)
    outer_rgb = cv2.cvtColor(outer_pixels.reshape(1, -1, 3), cv2.COLOR_BGR2RGB)
    
    # 绘制内圆像素
    plt.subplot(211)
    plt.imshow(inner_rgb, aspect='auto')
    plt.title("inner (360°)")
    plt.xlabel("angle (°)")
    plt.ylabel("RGB")
    plt.xticks(np.linspace(0, 359, 12), np.linspace(0, 330, 12, dtype=int))
    
    # 绘制外圆像素
    plt.subplot(212)
    plt.imshow(outer_rgb, aspect='auto')
    plt.title("outer (360°)")
    plt.xlabel("angle (°)")
    plt.ylabel("RGB")
    plt.xticks(np.linspace(0, 359, 12), np.linspace(0, 330, 12, dtype=int))
    
    plt.tight_layout()
    plt.show()
    
    # 打印统计信息
    print(f"内圆像素形状: {inner_pixels.shape}")
    print(f"外圆像素形状: {outer_pixels.shape}")
    print(f"内圆像素均值: {np.mean(inner_pixels, axis=0)}")
    print(f"外圆像素均值: {np.mean(outer_pixels, axis=0)}")


# 1 分割正方向的内外圆
# extract_inner_outer_circle("imgs/demo_i.png", 260, 290)

#2 读取图片中内外圆圆周上360°的像素点
inner_pixels, outer_pixels = get_circle_pixels("得出大小圆圆周的像素\imgs\demo_c.png", 262, 290)
visualize_circle_pixels(inner_pixels, outer_pixels)

