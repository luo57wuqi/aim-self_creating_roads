from PIL import Image, ImageDraw
import numpy as np
from math import sqrt

def basic_circle_analysis(image_path):
    """基础的圆形像素分析"""
    # 读取图片
    img = Image.open(image_path)
    img_array = np.array(img)
    
    print(f"=== 圆形对齐像素分析 ===")
    print(f"图片尺寸: {img.size}")
    print(f"图片模式: {img.mode}")
    print(f"数组形状: {img_array.shape}")
    
    # 转换为灰度
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2).astype(np.uint8)
    else:
        gray = img_array
    
    print(f"\n像素亮度统计:")
    print(f"最小亮度: {np.min(gray)}")
    print(f"最大亮度: {np.max(gray)}")
    print(f"平均亮度: {np.mean(gray):.1f}")
    print(f"亮度中位数: {np.median(gray):.1f}")
    
    # 使用多个阈值进行分割分析
    thresholds = [60, 80, 100, 120, 140]
    
    for thresh in thresholds:
        binary = gray < thresh
        
        if np.sum(binary) > 100:  # 至少有100个暗像素
            print(f"\n--- 阈值 {thresh} 分析 ---")
            print(f"暗像素数量: {np.sum(binary)}")
            print(f"暗像素比例: {np.sum(binary) / gray.size * 100:.1f}%")
            
            # 找到暗像素坐标
            dark_y, dark_x = np.where(binary)
            
            # 计算几何中心
            center_y = np.mean(dark_y)
            center_x = np.mean(dark_x)
            print(f"几何中心: ({center_x:.1f}, {center_y:.1f})")
            
            # 计算到中心的距离
            distances = []
            for y, x in zip(dark_y, dark_x):
                dist = sqrt((x - center_x)**2 + (y - center_y)**2)
                distances.append(dist)
            
            distances = np.array(distances)
            
            # 分析距离分布
            min_dist = np.min(distances)
            max_dist = np.max(distances)
            mean_dist = np.mean(distances)
            std_dist = np.std(distances)
            
            print(f"距离分析:")
            print(f"  最小距离: {min_dist:.1f}")
            print(f"  最大距离: {max_dist:.1f}")
            print(f"  平均距离: {mean_dist:.1f}")
            print(f"  距离标准差: {std_dist:.1f}")
            
            # 寻找距离分布的峰值
            hist, bin_edges = np.histogram(distances, bins=20)
            peak_idx = np.argmax(hist)
            estimated_radius = (bin_edges[peak_idx] + bin_edges[peak_idx + 1]) / 2
            
            print(f"估计半径: {estimated_radius:.1f} 像素")
            
            # 分析内外区域
            inner_mask = distances < estimated_radius * 0.8
            outer_mask = (distances >= estimated_radius * 0.8) & (distances <= estimated_radius * 1.2)
            
            inner_count = np.sum(inner_mask)
            outer_count = np.sum(outer_mask)
            
            print(f"内区域像素: {inner_count}")
            print(f"外区域像素: {outer_count}")
            
            if inner_count > 50 and outer_count > 50:
                # 分别计算内外区域的平均亮度
                inner_brightness = np.mean(gray[dark_y[inner_mask], dark_x[inner_mask]])
                outer_brightness = np.mean(gray[dark_y[outer_mask], dark_x[outer_mask]])
                
                print(f"内区域亮度: {inner_brightness:.1f}")
                print(f"外区域亮度: {outer_brightness:.1f}")
                print(f"亮度差异: {abs(inner_brightness - outer_brightness):.1f}")
                
                # 如果亮度差异明显，可能是内外圆
                if abs(inner_brightness - outer_brightness) > 15:
                    print("🔍 检测到可能的内外圆结构")
                    
                    # 分别计算内外圆中心
                    if inner_count > 0:
                        inner_center_y = np.mean(dark_y[inner_mask])
                        inner_center_x = np.mean(dark_x[inner_mask])
                        print(f"内圆中心: ({inner_center_x:.1f}, {inner_center_y:.1f})")
                    
                    if outer_count > 0:
                        outer_center_y = np.mean(dark_y[outer_mask])
                        outer_center_x = np.mean(dark_x[outer_mask])
                        print(f"外圆中心: ({outer_center_x:.1f}, {outer_center_y:.1f})")
                    
                    # 计算偏移
                    if inner_count > 0 and outer_count > 0:
                        offset = sqrt((inner_center_x - outer_center_x)**2 + 
                                    (inner_center_y - outer_center_y)**2)
                        print(f"圆心偏移: {offset:.2f} 像素")
                        
                        if offset < 3:
                            print("✅ 内外圆对齐良好")
                        else:
                            print("❌ 内外圆存在偏移")
                            
                            # 判断偏移方向
                            dx = inner_center_x - outer_center_x
                            dy = inner_center_y - outer_center_y
                            
                            direction = ""
                            if abs(dx) > abs(dy):
                                direction += "右" if dx > 0 else "左"
                            else:
                                direction += "下" if dy > 0 else "上"
                            
                            print(f"偏移方向: {direction}")
                    
                    return True  # 找到内外圆结构
    
    return False  # 未找到明显的内外圆结构

def edge_based_analysis(image_path):
    """基于边缘检测的分析"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    print(f"\n=== 边缘检测分析 ===")
    
    # 转换为灰度
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2).astype(np.uint8)
    else:
        gray = img_array
    
    # 简单的边缘检测（计算梯度）
    gy, gx = np.gradient(gray.astype(float))
    edge_magnitude = np.sqrt(gx**2 + gy**2)
    
    print(f"边缘强度统计:")
    print(f"最小边缘强度: {np.min(edge_magnitude):.1f}")
    print(f"最大边缘强度: {np.max(edge_magnitude):.1f}")
    print(f"平均边缘强度: {np.mean(edge_magnitude):.1f}")
    
    # 找到强边缘点
    edge_threshold = np.mean(edge_magnitude) + 2 * np.std(edge_magnitude)
    strong_edges = edge_magnitude > edge_threshold
    
    print(f"边缘阈值: {edge_threshold:.1f}")
    print(f"强边缘点数量: {np.sum(strong_edges)}")
    
    if np.sum(strong_edges) > 100:
        # 找到边缘点的坐标
        edge_y, edge_x = np.where(strong_edges)
        
        # 计算边缘点的中心
        center_y = np.mean(edge_y)
        center_x = np.mean(edge_x)
        
        print(f"边缘中心: ({center_x:.1f}, {center_y:.1f})")
        
        # 计算边缘点到中心的距离
        distances = []
        for y, x in zip(edge_y, edge_x):
            dist = sqrt((x - center_x)**2 + (y - center_y)**2)
            distances.append(dist)
        
        distances = np.array(distances)
        
        # 分析距离分布
        hist, bin_edges = np.histogram(distances, bins=30)
        
        # 寻找峰值（对应圆形边界）
        peaks = []
        for i in range(1, len(hist)-1):
            if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > np.mean(hist):
                peaks.append(i)
        
        print(f"检测到 {len(peaks)} 个距离峰值")
        
        for i, peak_idx in enumerate(peaks):
            radius = (bin_edges[peak_idx] + bin_edges[peak_idx + 1]) / 2
            print(f"峰值 {i+1}: 半径 ≈ {radius:.1f} 像素")
        
        if len(peaks) >= 2:
            print("🔍 检测到多个圆形边界")
            
            # 计算不同半径圆的中心
            radii = []
            for peak_idx in peaks[:2]:  # 取前两个峰值
                radius = (bin_edges[peak_idx] + bin_edges[peak_idx + 1]) / 2
                radii.append(radius)
            
            print(f"检测到的半径: {radii}")
            
            # 这里可以进一步分析内外圆的对齐情况
            if len(radii) == 2:
                print("可能是内外圆结构")
                
    return True

if __name__ == "__main__":
    image_path = "截圆.png"
    
    print("开始圆形像素对齐分析...")
    
    # 基础分析
    found_circles = basic_circle_analysis(image_path)
    
    if not found_circles:
        print("\n基础分析未找到明显内外圆，尝试边缘检测...")
        edge_based_analysis(image_path)
    
    print("\n分析完成！")