import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import argparse

def calculate_alignment_score(inner_pixels, outer_pixels):
    """
    计算内外圆像素值曲线的对齐程度（归一化互相关）
    
    参数:
        inner_pixels: 内圆圆周像素值列表 (1D numpy array)
        outer_pixels: 外圆圆周像素值列表 (1D numpy array)
        
    返回:
        best_score: 最佳对齐分数
        best_shift: 最佳对齐的偏移量 (对应角度)
    """
    best_score = -1
    best_shift = 0
    
    if len(inner_pixels) != len(outer_pixels):
        raise ValueError("Inner and outer pixel arrays must have the same length.")
        
    num_points = len(inner_pixels)
    
    for shift in range(num_points):
        rotated_inner_pixels = np.roll(inner_pixels, shift)
        
        mean_inner = np.mean(rotated_inner_pixels)
        mean_outer = np.mean(outer_pixels)
        
        centered_inner = rotated_inner_pixels - mean_inner
        centered_outer = outer_pixels - mean_outer
        
        numerator = np.sum(centered_inner * centered_outer)
        denominator = np.sqrt(np.sum(centered_inner**2) * np.sum(centered_outer**2))
        
        if denominator == 0:
            score = 0
        else:
            score = numerator / denominator
        
        if score > best_score:
            best_score = score
            best_shift = shift
            
    return best_score, best_shift


def get_circle_pixels_from_image(
    img, 
    diameter, 
    num_points=360, 
    channel='gray'  # 新增：通道选择，可选 'gray'/'R'/'G'/'B'
):
    """
    从已加载的图片中读取圆周上360°的像素点（支持灰度和RGB单通道）
    
    参数:
        img: 已加载的图片对象 (numpy array)
        diameter: 圆的直径
        num_points: 采样点数（默认360，对应360°）
        channel: 提取通道，可选 'gray'（灰度）、'R'、'G'、'B'
    
    返回:
        pixels: 圆周像素值列表 (形状: (num_points,))
    """
    if img is None:
        raise ValueError("图片对象为空。")
    
    h, w = img.shape[:2]
    center = (w // 2, h // 2)  # 图像中心
    radius = diameter // 2

    # 根据通道提取像素值
    if channel == 'gray':
        # 转换为灰度图 (单通道)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        get_pixel = lambda y, x: img[y, x] if (0 <= x < w and 0 <= y < h) else 0
    else:
        # 提取RGB通道（OpenCV是BGR格式，需映射）
        channel_map = {'B': 0, 'G': 1, 'R': 2}
        if channel not in channel_map:
            raise ValueError(f"通道 {channel} 无效，可选: 'gray'/'R'/'G'/'B'")
        c = channel_map[channel]
        get_pixel = lambda y, x: img[y, x, c] if (0 <= x < w and 0 <= y < h) else 0

    # 生成360°均匀分布的角度（弧度制）
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    pixels = []

    for angle in angles:
        # 计算圆周坐标
        x = int(center[0] + radius * np.cos(angle))
        y = int(center[1] + radius * np.sin(angle))
        pixels.append(get_pixel(y, x))

    return np.array(pixels)

def plot_alignment_score_chart(angles, scores, title="内圆旋转角度与归一化互相关得分曲线"):
    """
    绘制内圆旋转角度与归一化互相关得分的折线图
    
    参数:
        angles: 旋转角度列表
        scores: 归一化互相关得分列表
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    plt.plot(angles, scores, marker='o', linestyle='-', color='green', linewidth=1.5, markersize=4)
    plt.title(title, fontsize=14)
    plt.xlabel('旋转角度 (°)', fontsize=12)
    plt.ylabel('归一化互相关得分', fontsize=12)
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Analyze alignment scores of rotated inner circles with an original outer circle.")
    parser.add_argument('--original_image', type=str, required=True, help='Path to the original image file.')
    parser.add_argument('--rotated_images_folder', type=str, required=True, help='Path to the folder containing rotated inner circle images.')
    parser.add_argument('--inner_diameter', type=int, default=100, help='Diameter of the inner circle.')
    parser.add_argument('--outer_diameter', type=int, default=200, help='Diameter of the outer circle.')
    parser.add_argument('--channel', type=str, default='gray', choices=['gray', 'R', 'G', 'B'], help='Channel to analyze (gray, R, G, B).')
    args = parser.parse_args()

    original_image_path = args.original_image
    rotated_images_folder = args.rotated_images_folder
    inner_d = args.inner_diameter
    outer_d = args.outer_diameter
    channel = args.channel

    # 加载原始图片并提取外圆像素
    # original_img = cv2.imread(original_image_path)
    original_img = cv2.imdecode(np.fromfile(original_image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if original_img is None:
        raise ValueError(f"无法读取原始图像: {original_image_path}")
    outer_pixels_original = get_circle_pixels_from_image(original_img, outer_d, channel=channel)

    alignment_scores = []
    rotation_angles = []

    # 遍历旋转图片文件夹
    import os
    for filename in sorted(os.listdir(rotated_images_folder)):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            rotated_image_path = os.path.join(rotated_images_folder, filename)
            # rotated_img = cv2.imread(rotated_image_path)
            rotated_img = cv2.imdecode(np.fromfile(rotated_image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if rotated_img is None:
                print(f"警告: 无法读取旋转图像: {rotated_image_path}")
                continue
            
            # 提取旋转图片的内圆像素
            inner_pixels_rotated = get_circle_pixels_from_image(rotated_img, inner_d, channel=channel)
            
            # 计算对齐分数
            score, _ = calculate_alignment_score(inner_pixels_rotated, outer_pixels_original)
            alignment_scores.append(score)
            
            # 从文件名中提取旋转角度 (假设文件名格式为 inner_rotated_X.png)
            try:
                angle_str = filename.split('_')[-1].split('.')[0]
                rotation_angles.append(int(angle_str))
            except:
                rotation_angles.append(len(rotation_angles)) # 如果无法解析角度，使用序号

    # 绘制得分曲线
    if rotation_angles and alignment_scores:
        plot_alignment_score_chart(rotation_angles, alignment_scores)
    else:
        print("没有找到有效的旋转图片或无法计算得分。")