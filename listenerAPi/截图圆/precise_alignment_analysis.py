from PIL import Image, ImageDraw
import numpy as np
from math import sqrt

def precise_circle_detection(image_path):
    """精确的圆形检测和对齐分析"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    print(f"=== 精确圆形对齐分析 ===")
    print(f"图片尺寸: {img.size}")
    
    # 转换为灰度
    if len(img_array.shape) == 3:
        # 处理RGBA图片，只取RGB通道
        rgb = img_array[:,:,:3]
        gray = np.mean(rgb, axis=2).astype(np.uint8)
    else:
        gray = img_array
    
    print(f"灰度范围: {np.min(gray)} - {np.max(gray)}")
    
    # 使用自适应阈值分割
    # 计算局部平均值作为自适应阈值
    kernel_size = 15
    from scipy import ndimage
    local_mean = ndimage.uniform_filter(gray, size=kernel_size)
    
    # 自适应阈值分割
    adaptive_binary = gray < (local_mean - 10)
    
    print(f"自适应阈值分割结果:")
    print(f"暗像素数量: {np.sum(adaptive_binary)}")
    print(f"暗像素比例: {np.sum(adaptive_binary) / gray.size * 100:.1f}%")
    
    # 找到连通区域
    labeled, num_features = ndimage.label(adaptive_binary)
    print(f"检测到 {num_features} 个连通区域")
    
    # 分析每个连通区域
    circles = []
    
    for region_id in range(1, num_features + 1):
        region_mask = labeled == region_id
        pixels = np.where(region_mask)
        
        if len(pixels[0]) > 500:  # 只分析较大的区域
            # 计算区域属性
            y_coords = pixels[0]
            x_coords = pixels[1]
            
            # 计算中心
            center_y = np.mean(y_coords)
            center_x = np.mean(x_coords)
            
            # 计算等效半径
            area = len(pixels[0])
            equivalent_radius = np.sqrt(area / np.pi)
            
            # 计算圆度（形状接近圆形的程度）
            # 计算边界点
            from scipy import ndimage
            boundary = ndimage.binary_erosion(region_mask) != region_mask
            boundary_pixels = np.where(boundary)
            
            if len(boundary_pixels[0]) > 0:
                # 计算边界点到中心的距离标准差
                boundary_distances = []
                for by, bx in zip(boundary_pixels[0], boundary_pixels[1]):
                    dist = sqrt((bx - center_x)**2 + (by - center_y)**2)
                    boundary_distances.append(dist)
                
                boundary_distances = np.array(boundary_distances)
                circularity = 1 - (np.std(boundary_distances) / np.mean(boundary_distances))
                
                # 计算平均亮度
                mean_brightness = np.mean(gray[pixels])
                
                circles.append({
                    'center': (center_x, center_y),
                    'radius': equivalent_radius,
                    'area': area,
                    'circularity': circularity,
                    'brightness': mean_brightness,
                    'pixels': (y_coords, x_coords)
                })
                
                print(f"\n区域 {region_id}:")
                print(f"  中心: ({center_x:.1f}, {center_y:.1f})")
                print(f"  等效半径: {equivalent_radius:.1f} 像素")
                print(f"  面积: {area} 像素")
                print(f"  圆度: {circularity:.3f}")
                print(f"  平均亮度: {mean_brightness:.1f}")
    
    # 按圆度排序，找出最圆的区域
    circles.sort(key=lambda x: x['circularity'], reverse=True)
    
    print(f"\n=== 圆形结构分析 ===")
    
    if len(circles) >= 2:
        # 找到最可能的内外圆组合
        best_pair = None
        best_score = 0
        
        for i in range(len(circles)):
            for j in range(i+1, len(circles)):
                c1, c2 = circles[i], circles[j]
                
                # 计算两个圆的中心距离
                dx = c1['center'][0] - c2['center'][0]
                dy = c1['center'][1] - c2['center'][1]
                center_distance = sqrt(dx**2 + dy**2)
                
                # 计算半径比例
                radius_ratio = max(c1['radius'], c2['radius']) / min(c1['radius'], c2['radius'])
                
                # 计算亮度差异
                brightness_diff = abs(c1['brightness'] - c2['brightness'])
                
                # 评分函数（中心距离越小越好，半径比例在1.2-2.0之间最好，亮度差异越大越好）
                score = 0
                
                # 中心距离评分（小于5像素得满分）
                if center_distance < 5:
                    score += 50
                elif center_distance < 10:
                    score += 30
                elif center_distance < 20:
                    score += 10
                
                # 半径比例评分
                if 1.2 <= radius_ratio <= 2.0:
                    score += 30
                elif 1.0 <= radius_ratio <= 2.5:
                    score += 15
                
                # 亮度差异评分
                if brightness_diff > 20:
                    score += 20
                elif brightness_diff > 10:
                    score += 10
                
                # 圆度评分
                avg_circularity = (c1['circularity'] + c2['circularity']) / 2
                score += avg_circularity * 20
                
                if score > best_score:
                    best_score = score
                    best_pair = (c1, c2, center_distance, radius_ratio, brightness_diff)
        
        if best_pair:
            c1, c2, center_distance, radius_ratio, brightness_diff = best_pair
            
            print(f"\n🎯 最佳内外圆匹配:")
            print(f"圆1 (可能是外圆):")
            print(f"  中心: ({c1['center'][0]:.1f}, {c1['center'][1]:.1f})")
            print(f"  半径: {c1['radius']:.1f} 像素")
            print(f"  圆度: {c1['circularity']:.3f}")
            print(f"  亮度: {c1['brightness']:.1f}")
            
            print(f"\n圆2 (可能是内圆):")
            print(f"  中心: ({c2['center'][0]:.1f}, {c2['center'][1]:.1f})")
            print(f"  半径: {c2['radius']:.1f} 像素")
            print(f"  圆度: {c2['circularity']:.3f}")
            print(f"  亮度: {c2['brightness']:.1f}")
            
            print(f"\n对齐分析:")
            print(f"  圆心距离: {center_distance:.2f} 像素")
            print(f"  半径比例: {radius_ratio:.2f}")
            print(f"  亮度差异: {brightness_diff:.1f}")
            
            # 最终对齐判断
            alignment_threshold = 5  # 5像素以内认为对齐
            if center_distance <= alignment_threshold:
                print(f"  ✅ 内外圆对齐: 是 (距离 ≤ {alignment_threshold}像素)")
            else:
                print(f"  ❌ 内外圆对齐: 否 (距离 > {alignment_threshold}像素)")
                
                # 判断偏移方向
                dx = c2['center'][0] - c1['center'][0]
                dy = c2['center'][1] - c1['center'][1]
                
                direction = ""
                if abs(dx) > abs(dy):
                    direction += "右" if dx > 0 else "左"
                else:
                    direction += "下" if dy > 0 else "上"
                
                print(f"  偏移方向: {direction}")
                print(f"  偏移量: ({dx:.1f}, {dy:.1f})")
            
            return True, c1, c2, center_distance
        else:
            print("未找到合适的内外圆组合")
            return False, None, None, None
    
    elif len(circles) == 1:
        print("只检测到一个圆形区域")
        c = circles[0]
        print(f"中心: ({c['center'][0]:.1f}, {c['center'][1]:.1f})")
        print(f"半径: {c['radius']:.1f} 像素")
        print("可能是单一圆形或内外圆完全重合")
        return True, c, c, 0.0
    
    else:
        print("未检测到明显的圆形区域")
        return False, None, None, None

if __name__ == "__main__":
    image_path = "截圆.png"
    
    print("开始精确的圆形对齐分析...")
    
    try:
        success, outer_circle, inner_circle, distance = precise_circle_detection(image_path)
        
        if success:
            print(f"\n分析完成！")
            if distance > 0:
                print(f"圆心偏移: {distance:.2f} 像素")
            else:
                print("圆心完全对齐")
        else:
            print("\n未能检测到完整的内外圆结构")
            
    except ImportError:
        print("需要安装scipy库进行高级分析")
        print("请运行: pip install scipy")
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")