from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

def analyze_circle_pixels(image_path):
    """通过像素分析判断圆形对齐"""
    # 读取图片
    img = Image.open(image_path)
    img_array = np.array(img)
    
    print(f"图片尺寸: {img.size}")
    print(f"图片模式: {img.mode}")
    print(f"数组形状: {img_array.shape}")
    
    # 转换为灰度图
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2).astype(np.uint8)
    else:
        gray = img_array
    
    # 分析像素亮度分布
    print(f"\n像素亮度统计:")
    print(f"最小亮度: {np.min(gray)}")
    print(f"最大亮度: {np.max(gray)}")
    print(f"平均亮度: {np.mean(gray):.1f}")
    print(f"亮度中位数: {np.median(gray):.1f}")
    
    # 使用阈值分割找到暗色区域（圆形）
    threshold = np.mean(gray) - 20  # 低于平均值20的认为是圆形区域
    binary = gray < threshold
    
    print(f"\n使用阈值: {threshold:.1f}")
    print(f"暗像素数量: {np.sum(binary)}")
    print(f"暗像素比例: {np.sum(binary) / gray.size * 100:.1f}%")
    
    # 找到所有暗像素的坐标
    dark_pixels = np.where(binary)
    if len(dark_pixels[0]) == 0:
        print("未找到暗色区域")
        return
    
    # 计算暗像素的几何中心
    center_y = np.mean(dark_pixels[0])
    center_x = np.mean(dark_pixels[1])
    
    print(f"\n暗区域几何中心: ({center_x:.1f}, {center_y:.1f})")
    
    # 计算从中心到各暗像素的距离
    distances = []
    for y, x in zip(dark_pixels[0], dark_pixels[1]):
        dist = sqrt((x - center_x)**2 + (y - center_y)**2)
        distances.append(dist)
    
    distances = np.array(distances)
    
    # 分析距离分布来识别圆形
    print(f"\n距离分析:")
    print(f"最小距离: {np.min(distances):.1f}")
    print(f"最大距离: {np.max(distances):.1f}")
    print(f"平均距离: {np.mean(distances):.1f}")
    print(f"距离标准差: {np.std(distances):.1f}")
    
    # 寻找距离分布的峰值（对应圆形半径）
    hist, bins = np.histogram(distances, bins=50)
    peak_bin = np.argmax(hist)
    estimated_radius = (bins[peak_bin] + bins[peak_bin + 1]) / 2
    
    print(f"\n估计的圆形半径: {estimated_radius:.1f} 像素")
    
    # 通过分析不同区域的像素分布来判断是否有多个同心圆
    inner_threshold = estimated_radius * 0.7
    outer_threshold = estimated_radius * 1.3
    
    inner_pixels = distances < inner_threshold
    outer_pixels = (distances >= inner_threshold) & (distances <= outer_threshold)
    
    print(f"\n区域分析:")
    print(f"内区域像素数: {np.sum(inner_pixels)}")
    print(f"外区域像素数: {np.sum(outer_pixels)}")
    
    # 计算内外区域的亮度差异
    inner_brightness = np.mean(gray[dark_pixels[0][inner_pixels], dark_pixels[1][inner_pixels]])
    outer_brightness = np.mean(gray[dark_pixels[0][outer_pixels], dark_pixels[1][outer_pixels]])
    
    print(f"\n亮度分析:")
    print(f"内区域平均亮度: {inner_brightness:.1f}")
    print(f"外区域平均亮度: {outer_brightness:.1f}")
    print(f"亮度差异: {abs(inner_brightness - outer_brightness):.1f}")
    
    # 判断是否可能是同心圆
    brightness_diff = abs(inner_brightness - outer_brightness)
    if brightness_diff > 10:  # 亮度差异较大，可能是不同圆
        print(f"\n🔍 检测到可能的内外圆结构")
        print(f"   亮度差异: {brightness_diff:.1f} ( > 10)")
        
        # 分别计算内外圆的中心
        if np.sum(inner_pixels) > 0:
            inner_center_y = np.mean(dark_pixels[0][inner_pixels])
            inner_center_x = np.mean(dark_pixels[1][inner_pixels])
            print(f"   内圆中心: ({inner_center_x:.1f}, {inner_center_y:.1f})")
        else:
            inner_center_y, inner_center_x = center_y, center_x
        
        if np.sum(outer_pixels) > 0:
            outer_center_y = np.mean(dark_pixels[0][outer_pixels])
            outer_center_x = np.mean(dark_pixels[1][outer_pixels])
            print(f"   外圆中心: ({outer_center_x:.1f}, {outer_center_y:.1f})")
        else:
            outer_center_y, outer_center_x = center_y, center_x
        
        # 计算圆心偏移
        offset = sqrt((inner_center_x - outer_center_x)**2 + (inner_center_y - outer_center_y)**2)
        print(f"   圆心偏移: {offset:.2f} 像素")
        
        if offset < 3:  # 3像素以内认为对齐
            print(f"   ✅ 内外圆对齐良好")
        else:
            print(f"   ❌ 内外圆存在偏移")
            print(f"      偏移方向: {'右' if inner_center_x > outer_center_x else '左'}{ '下' if inner_center_y > outer_center_y else '上'}")
    
    else:
        print(f"\n❓ 未检测到明显的内外圆结构")
        print(f"   可能是单一圆形或对齐度很高")
    
    # 可视化结果
    plt.figure(figsize=(15, 10))
    
    # 原图
    plt.subplot(2, 3, 1)
    plt.imshow(img_array)
    plt.title('原始图片')
    plt.axis('off')
    
    # 灰度图
    plt.subplot(2, 3, 2)
    plt.imshow(gray, cmap='gray')
    plt.title('灰度图')
    plt.axis('off')
    
    # 二值图
    plt.subplot(2, 3, 3)
    plt.imshow(binary, cmap='binary')
    plt.title(f'二值图 (阈值={threshold:.0f})')
    plt.axis('off')
    
    # 距离分布图
    plt.subplot(2, 3, 4)
    plt.hist(distances, bins=50, alpha=0.7, color='blue')
    plt.axvline(estimated_radius, color='red', linestyle='--', label=f'估计半径: {estimated_radius:.1f}')
    plt.xlabel('距离 (像素)')
    plt.ylabel('像素数量')
    plt.title('像素距离分布')
    plt.legend()
    
    # 圆形检测结果
    plt.subplot(2, 3, 5)
    result_img = img_array.copy()
    
    # 绘制检测到的圆形
    if len(img_array.shape) == 3:
        result_img = Image.fromarray(result_img)
        draw = ImageDraw.Draw(result_img)
        
        # 绘制几何中心
        draw.ellipse([center_x-5, center_y-5, center_x+5, center_y+5], fill='red', outline='red')
        
        # 绘制估计的圆形
        draw.ellipse([center_x-estimated_radius, center_y-estimated_radius, 
                     center_x+estimated_radius, center_y+estimated_radius], 
                    outline='green', width=3)
        
        result_img = np.array(result_img)
    
    plt.imshow(result_img)
    plt.title('圆形检测结果')
    plt.axis('off')
    
    # 像素分布热力图
    plt.subplot(2, 3, 6)
    plt.scatter(dark_pixels[1][::100], dark_pixels[0][::100], c=distances[::100], 
               cmap='viridis', alpha=0.6, s=1)
    plt.colorbar(label='到中心距离')
    plt.scatter(center_x, center_y, c='red', s=100, marker='x', label='几何中心')
    plt.xlabel('X坐标')
    plt.ylabel('Y坐标')
    plt.title('像素分布热力图')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('circle_pixel_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return center_x, center_y, estimated_radius

def advanced_circle_detection(image_path):
    """更高级的圆形检测方法"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # 转换为灰度
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2).astype(np.uint8)
    else:
        gray = img_array
    
    print("\n=== 高级圆形检测分析 ===")
    
    # 使用不同的阈值进行分割
    thresholds = [50, 80, 100, 120, 150]
    
    for i, thresh in enumerate(thresholds):
        binary = gray < thresh
        
        # 找到连通区域
        from scipy import ndimage
        labeled, num_features = ndimage.label(binary)
        
        print(f"\n阈值 {thresh}:")
        print(f"  检测到 {num_features} 个连通区域")
        
        if num_features > 0:
            # 分析每个区域
            for region_id in range(1, num_features + 1):
                region_mask = labeled == region_id
                pixels = np.where(region_mask)
                
                if len(pixels[0]) > 100:  # 只分析较大的区域
                    center_y = np.mean(pixels[0])
                    center_x = np.mean(pixels[1])
                    
                    # 计算等效半径
                    area = len(pixels[0])
                    equivalent_radius = np.sqrt(area / np.pi)
                    
                    print(f"    区域 {region_id}:")
                    print(f"      中心: ({center_x:.1f}, {center_y:.1f})")
                    print(f"      面积: {area} 像素")
                    print(f"      等效半径: {equivalent_radius:.1f} 像素")

if __name__ == "__main__":
    image_path = "截圆.png"
    
    print("开始像素级别的圆形对齐分析...")
    
    # 基础分析
    center_x, center_y, radius = analyze_circle_pixels(image_path)
    
    # 高级分析（如果有scipy）
    try:
        advanced_circle_detection(image_path)
    except ImportError:
        print("\n未安装scipy，跳过高级分析")
    
    print("\n分析完成！")