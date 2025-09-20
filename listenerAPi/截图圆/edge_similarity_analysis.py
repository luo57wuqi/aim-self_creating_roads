from PIL import Image
import numpy as np
from math import sqrt
from scipy import ndimage

def edge_similarity_analysis(image_path):
    """比较内外圆的边缘相似度"""
    img = Image.open(image_path)
    img_array = np.array(img)

    print("=== 内外圆边缘相似度分析 ===")

    # 转换为灰度图
    if len(img_array.shape) == 3:
        gray = np.mean(img_array[:, :, :3], axis=2).astype(np.uint8)
    else:
        gray = img_array

    # 使用梯度计算边缘
    gy, gx = np.gradient(gray.astype(float))
    edge_magnitude = np.sqrt(gx**2 + gy**2)

    # 阈值分割边缘
    edge_threshold = np.mean(edge_magnitude) + 2 * np.std(edge_magnitude)
    strong_edges = edge_magnitude > edge_threshold

    print(f"边缘阈值: {edge_threshold:.1f}")
    print(f"强边缘点数量: {np.sum(strong_edges)}")

    # 找到连通区域
    labeled, num_features = ndimage.label(strong_edges)
    print(f"检测到 {num_features} 个边缘区域")

    # 分析每个区域
    circles = []
    for region_id in range(1, num_features + 1):
        region_mask = labeled == region_id
        pixels = np.where(region_mask)

        if len(pixels[0]) > 500:  # 只分析较大的区域
            # 计算中心
            center_y = np.mean(pixels[0])
            center_x = np.mean(pixels[1])

            # 计算等效半径
            area = len(pixels[0])
            equivalent_radius = np.sqrt(area / np.pi)

            # 计算边界点到中心的距离
            distances = []
            for y, x in zip(pixels[0], pixels[1]):
                dist = sqrt((x - center_x)**2 + (y - center_y)**2)
                distances.append(dist)

            distances = np.array(distances)

            # 计算边缘分布的标准差
            edge_std = np.std(distances)

            circles.append({
                'center': (center_x, center_y),
                'radius': equivalent_radius,
                'area': area,
                'edge_std': edge_std,
                'pixels': pixels
            })

            print(f"\n区域 {region_id}:")
            print(f"  中心: ({center_x:.1f}, {center_y:.1f})")
            print(f"  等效半径: {equivalent_radius:.1f} 像素")
            print(f"  面积: {area} 像素")
            print(f"  边缘分布标准差: {edge_std:.2f}")

    # 比较内外圆的边缘相似度
    if len(circles) >= 2:
        # 假设第一个区域是外圆，第二个区域是内圆
        outer_circle = circles[0]
        inner_circle = circles[1]

        print("\n=== 内外圆边缘相似度 ===")
        print(f"外圆边缘标准差: {outer_circle['edge_std']:.2f}")
        print(f"内圆边缘标准差: {inner_circle['edge_std']:.2f}")

        similarity = 1 - abs(outer_circle['edge_std'] - inner_circle['edge_std']) / max(outer_circle['edge_std'], inner_circle['edge_std'])
        print(f"边缘相似度: {similarity:.2f}")

        if similarity > 0.8:
            print("✅ 内外圆边缘高度相似")
        else:
            print("❌ 内外圆边缘不相似")

    else:
        print("未检测到足够的内外圆边缘区域")

if __name__ == "__main__":
    image_path = r"C:\Users\admin\Desktop\RPA\skills\listenerAPi\截图圆\截圆.png"

    print("开始内外圆边缘相似度分析...")
    edge_similarity_analysis(image_path)