import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_circle_pixels(
    image_path, 
    inner_diameter, 
    outer_diameter, 
    num_points=360, 
    channel='gray'  # 新增：通道选择，可选 'gray'/'R'/'G'/'B'
):
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


def plot_grayscale_line_chart(
    inner_pixels, 
    outer_pixels, 
    channel='gray', 
    title="圆周像素值分布折线图"
):
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


from matplotlib.widgets import RadioButtons

if __name__ == '__main__':
    image_path = "c.png"
    inner_d = 261
    outer_d = 297

    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(left=0.25) # 为单选按钮留出空间

    # 初始绘制
    initial_channel = 'gray'
    inner_px, outer_px = get_circle_pixels(image_path, inner_d, outer_d, channel=initial_channel)
    line1, = ax.plot(inner_px, label='inner', color='blue', linewidth=1.5)
    line2, = ax.plot(outer_px, label='outer', color='red', linewidth=1.5)
    ax.set_title(f"innerouter ({initial_channel}channel)", fontsize=14)
    ax.set_xlabel('angele (°) / sample', fontsize=12)
    ax.set_ylabel(f'px (0-255)', fontsize=12)
    ax.set_ylim(0, 255)
    ax.legend(fontsize=12)
    ax.grid(linestyle='--', alpha=0.7)

    # 创建单选按钮区域
    rax = plt.axes([0.02, 0.7, 0.15, 0.15], facecolor='lightgoldenrodyellow')
    radio = RadioButtons(rax, ('gray', 'R', 'G', 'B'))

    def update(label):
        try:
            new_inner_px, new_outer_px = get_circle_pixels(image_path, inner_d, outer_d, channel=label)
            line1.set_ydata(new_inner_px)
            line2.set_ydata(new_outer_px)
            ax.set_title(f"内外圆圆周像素值分布 ({label}通道)", fontsize=14)
            fig.canvas.draw_idle()
        except ValueError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"运行异常: {e}")

    radio.on_clicked(update)

    plt.show()