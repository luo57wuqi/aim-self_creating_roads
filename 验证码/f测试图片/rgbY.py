import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import argparse

# Function to calculate normalized cross-correlation and best shift
def calculate_alignment_score(inner_curve, outer_curve):
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


# Function to extract pixel values along the circumference
def get_circle_pixels(image_path, inner_diameter, outer_diameter, channel='gray'):
    """
    读取图片中内外圆圆周上360°的像素点（支持灰度和RGB单通道）
    
    参数:
        image_path: 图片路径
        inner_diameter: 内圆直径
        outer_diameter: 外圆直径
        num_points: 采样点数（默认360，对应360°）
        channel: 提取通道，可选 'gray'（灰度）、'R'、'G'、'B'
    
    返回:
        inner_pixels: 内圆圆周像素值列表 (形状: (num_points,))
        outer_pixels: 外圆圆周像素值列表 (形状: (num_points,))
    """
    # 读取彩色图像（BGR格式）
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图像: {image_path}")
    
    h, w = img.shape[:2]
    center = (w // 2, h // 2)  # 图像中心
    inner_radius = inner_diameter // 2
    outer_radius = outer_diameter // 2

    # 根据通道提取像素值
    if channel == 'gray':
        # 转换为灰度图 (单通道)
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
    inner_pixels, outer_pixels = [], []

    for angle in angles:
        # 计算内圆圆周坐标
        x_in = int(center[0] + inner_radius * np.cos(angle))

        y_in = int(center[1] + inner_radius * np.sin(angle))
        inner_pixels.append(get_pixel(y_in, x_in))

        # 计算外圆圆周坐标
        x_out = int(center[0] + outer_radius * np.cos(angle))
        y_out = int(center[1] + outer_radius * np.sin(angle))
        outer_pixels.append(get_pixel(y_out, x_out))

    return np.array(inner_pixels), np.array(outer_pixels)


# Function to plot grayscale line chart
def plot_grayscale_line_chart(inner_pixels, outer_pixels, aligned_inner_pixels, channel_name, save_prefix):
    """
    绘制内外圆圆周像素值折线图（支持显示通道名称）
    
    参数:
        inner_pixels: 内圆圆周像素值列表
        outer_pixels: 外圆圆周像素值列表
        channel: 当前显示的通道（用于标题）
        title: 图表标题前缀
    """
    plt.figure(figsize=(12, 6))
    plt.plot(inner_pixels, label='内圆', color='blue', linewidth=1.5)
    plt.plot(outer_pixels, label='外圆', color='red', linewidth=1.5)
    plt.title(f"{title} ({channel}通道)", fontsize=14)
    plt.xlabel('角度 (°) / 采样点', fontsize=12)
    plt.ylabel('像素值 (0-255)', fontsize=12)
    plt.ylim(0, 255)  # 像素值范围固定0-255
    plt.legend(fontsize=12)
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze circumferential pixel values and alignment of inner and outer circles.")
    parser.add_argument('--image', type=str, default='demo_c.png', help='Path to the input image file (e.g., demo_c.png)')
    args = parser.parse_args()

    image_path = args.image

    # Define inner and outer circle diameters
    inner_d = 100  # Inner circle diameter
    outer_d = 150  # Outer circle diameter

    # 1. 提取灰度通道的像素数据
    inner_px_gray, outer_px_gray = get_circle_pixels(image_path, inner_d, outer_d, channel='gray')
    print(f"灰度通道内圆像素值: {inner_px_gray}")
    print(f"灰度通道外圆像素值: {outer_px_gray}")
    # 2. 计算灰度通道的对齐程度
    difference_gray = inner_px_gray - outer_px_gray
    print(f"灰度通道像素差值 (内圆 - 外圆): {difference_gray}")
    alignment_score_gray, best_shift_gray = calculate_alignment_score(inner_px_gray, outer_px_gray)
    print(f"灰度通道曲线对齐程度 (归一化互相关分数): {alignment_score_gray:.4f}")
    print(f"灰度通道最佳对齐偏移量 (采样点): {best_shift_gray}")


    for ch in ['R', 'G', 'B']:
        inner_px_ch, outer_px_ch = get_circle_pixels(image_path, inner_d, outer_d, channel=ch)
        alignment_score_ch, best_shift_ch = calculate_alignment_score(inner_px_ch, outer_px_ch)
        print(f"{ch} 通道曲线对齐程度 (归一化互相关分数): {alignment_score_ch:.4f}")
        print(f"{ch} 通道最佳对齐偏移量 (采样点): {best_shift_ch}")

        # 计算并打印RGB通道的像素差值
        difference_ch = inner_px_ch - outer_px_ch
        print(f"{ch} 通道像素差值 (内圆 - 外圆): {difference_ch}")

    plt.close()

    # 以下是交互式部分，如果需要可以取消注释
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), gridspec_kw={'height_ratios': [3, 1, 1]})
    plt.subplots_adjust(left=0.25, bottom=0.05, right=0.95, top=0.95, hspace=0.4) # 为单选按钮留出空间

    # 初始绘制像素值图
    initial_channel = 'gray'
    inner_px, outer_px = get_circle_pixels(image_path, inner_d, outer_d, channel=initial_channel)
    line1, = ax1.plot(inner_px, label='Inner Circle', color='blue', linewidth=1.5)
    line2, = ax1.plot(outer_px, label='Outer Circle', color='red', linewidth=1.5)
    ax1.set_title(f"Circumferential Pixel Value Distribution ({initial_channel} Channel)", fontsize=14)
    ax1.set_xlabel('Angle (°) / Sample Point', fontsize=12)
    ax1.set_ylabel(f'Pixel Value (0-255)', fontsize=12)
    ax1.set_ylim(0, 255)
    ax1.legend(fontsize=12)
    ax1.grid(linestyle='--', alpha=0.7)

    # 初始绘制差值图
    difference = inner_px - outer_px
    diff_line, = ax2.plot(difference, label='Difference (Inner - Outer)', color='green', linewidth=1.5)
    ax2.set_title('Pixel Value Difference', fontsize=14)
    ax2.set_xlabel('Angle (°) / Sample Point', fontsize=12)
    ax2.set_ylabel('Difference', fontsize=12)
    ax2.grid(linestyle='--', alpha=0.7)
    ax2.legend(fontsize=12)

    # 初始绘制一阶导数图
    inner_diff = np.diff(inner_px)
    outer_diff = np.diff(outer_px)
    diff_line_inner, = ax3.plot(inner_diff, label='Inner Circle Derivative', color='purple', linewidth=1.5)
    diff_line_outer, = ax3.plot(outer_diff, label='Outer Circle Derivative', color='orange', linewidth=1.5)
    ax3.set_title('First Order Derivative of Pixel Values', fontsize=14)
    ax3.set_xlabel('Angle (°) / Sample Point', fontsize=12)
    ax3.set_ylabel('Derivative', fontsize=12)
    ax3.grid(linestyle='--', alpha=0.7)
    ax3.legend(fontsize=12)

    # 创建单选按钮区域
    rax = plt.axes([0.02, 0.7, 0.15, 0.15], facecolor='lightgoldenrodyellow')
    radio = RadioButtons(rax, ('gray', 'R', 'G', 'B'))

    def update(label):
        try:
            new_inner_px, new_outer_px = get_circle_pixels(image_path, inner_d, outer_d, channel=label)
            line1.set_ydata(new_inner_px)
            line2.set_ydata(new_outer_px)
            ax1.set_title(f"Circumferential Pixel Value Distribution ({label} Channel)", fontsize=14)

            new_difference = new_inner_px - new_outer_px
            diff_line.set_ydata(new_difference)
            ax2.set_title('Pixel Value Difference', fontsize=14)

            # 更新一阶导数图
            new_inner_diff = np.diff(new_inner_px)
            new_outer_diff = np.diff(new_outer_px)
            diff_line_inner.set_ydata(new_inner_diff)
            diff_line_outer.set_ydata(new_outer_diff)
            ax3.set_title('First Order Derivative of Pixel Values', fontsize=14)

            # 计算并打印对齐分数和偏移量
            alignment_score, best_shift = calculate_alignment_score(new_inner_px, new_outer_px)
            print(f"\n{label} Channel Curve Alignment Score (Normalized Cross-Correlation): {alignment_score:.4f}")
            print(f"{label} Channel Best Alignment Shift (Sample Points): {best_shift}")
            print(f"{label} Channel Pixel Difference (Inner - Outer): {new_difference}")

            fig.canvas.draw_idle()
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Runtime Error: {e}")

    radio.on_clicked(update)

    plt.show()

