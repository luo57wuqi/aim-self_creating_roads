import os
import cv2
import numpy as np
import pandas as pd
import argparse
from ..f测试图片.检像素差值_传参数 import calculate_alignment_score, get_circle_pixels

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

# 主函数
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate alignment scores for a batch of rotated images and save to CSV.")
    parser.add_argument('--original_image', type=str, required=True, help='Path to the original image file.')
    parser.add_argument('--rotated_images_folder', type=str, required=True, help='Path to the folder containing rotated images.')
    parser.add_argument('--output_csv', type=str, default='alignment_scores.csv', help='Name of the output CSV file.')
    parser.add_argument('--inner_diameter', type=int, default=261, help='Diameter of the inner circle.')
    parser.add_argument('--outer_diameter', type=int, default=297, help='Diameter of the outer circle.')
    args = parser.parse_args()

    original_image_path = args.original_image
    rotated_images_folder = args.rotated_images_folder
    output_csv_path = os.path.join(rotated_images_folder, args.output_csv) # 将CSV保存到旋转图片文件夹内
    inner_d = args.inner_diameter
    outer_d = args.outer_diameter

    # 加载原始图片并提取外圆像素
    try:
        _, original_outer_pixels = get_circle_pixels(original_image_path, inner_d, outer_d, channel='gray')
    except ValueError as e:
        print(f"错误: {e}")
        exit()

    scores_data = []

    # 遍历旋转图片文件夹
    for filename in os.listdir(rotated_images_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
            rotated_image_path = os.path.join(rotated_images_folder, filename)
            try:
                # 提取旋转图片的内圆像素
                rotated_inner_pixels, _ = get_circle_pixels(rotated_image_path, inner_d, outer_d, channel='gray')
                
                # 计算归一化互相关得分
                alignment_score, _ = calculate_alignment_score(rotated_inner_pixels, original_outer_pixels)
                
                # 从文件名中提取旋转角度
                match = re.search(r'rotated_image_(\d+)deg', filename)
                rotation_angle = int(match.group(1)) if match else -1 # -1表示无法解析角度

                scores_data.append({'Image': filename, 'Rotation_Angle': rotation_angle, 'Alignment_Score': alignment_score})
                print(f"处理图片: {filename}, 归一化得分: {alignment_score:.4f}")

            except ValueError as e:
                print(f"处理图片 {filename} 时出错: {e}")
            except Exception as e:
                print(f"处理图片 {filename} 时发生未知错误: {e}")

    # 将结果保存到CSV
    if scores_data:
        df = pd.DataFrame(scores_data)
        df.to_csv(output_csv_path, index=False)
        print(f"归一化得分已保存到: {output_csv_path}")
    else:
        print("没有处理任何图片，未生成CSV文件。")