import cv2
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt

def find_circles_by_color(image_path):
    """通过颜色分析找到内外圆的圆心和半径"""
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("无法读取图片文件")
    
    # 转换为RGB格式用于显示
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 转换为HSV颜色空间，便于颜色分割
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 定义黑色的HSV范围（外圆）
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    
    # 定义灰色的HSV范围（内圆）
    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 50, 200])
    
    # 创建掩码
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
    
    # 找到轮廓
    contours_black, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_gray, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到最大的黑色轮廓（外圆）
    if contours_black:
        largest_black = max(contours_black, key=cv2.contourArea)
        (x1, y1), radius1 = cv2.minEnclosingCircle(largest_black)
        center1 = (int(x1), int(y1))
        radius1 = int(radius1)
    else:
        center1 = None
        radius1 = 0
    
    # 找到最大的灰色轮廓（内圆）
    if contours_gray:
        largest_gray = max(contours_gray, key=cv2.contourArea)
        (x2, y2), radius2 = cv2.minEnclosingCircle(largest_gray)
        center2 = (int(x2), int(y2))
        radius2 = int(radius2)
    else:
        center2 = None
        radius2 = 0
    
    return img_rgb, center1, radius1, center2, radius2, mask_black, mask_gray

def analyze_circle_alignment(image_path):
    """分析内外圆的对齐情况"""
    try:
        img_rgb, center1, radius1, center2, radius2, mask_black, mask_gray = find_circles_by_color(image_path)
        
        print("=== 圆形对齐分析结果 ===")
        print(f"图片尺寸: {img_rgb.shape[1]}x{img_rgb.shape[0]}")
        
        if center1 and center2:
            # 计算圆心距离
            distance = sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
            
            print(f"\n外圆信息:")
            print(f"  圆心: {center1}")
            print(f"  半径: {radius1}")
            
            print(f"\n内圆信息:")
            print(f"  圆心: {center2}")
            print(f"  半径: {radius2}")
            
            print(f"\n对齐分析:")
            print(f"  圆心距离: {distance:.2f} 像素")
            print(f"  半径差: {abs(radius1 - radius2)} 像素")
            
            # 判断是否对齐（阈值可以根据需要调整）
            alignment_threshold = 5  # 5像素以内认为对齐
            if distance <= alignment_threshold:
                print(f"  ✅ 圆心对齐: 是 (距离 ≤ {alignment_threshold}像素)")
            else:
                print(f"  ❌ 圆心对齐: 否 (距离 > {alignment_threshold}像素)")
                print(f"     偏移方向: ({'右' if center2[0] > center1[0] else '左'}{ '下' if center2[1] > center1[1] else '上'})")
            
            # 可视化结果
            plt.figure(figsize=(15, 10))
            
            # 原图
            plt.subplot(2, 3, 1)
            plt.imshow(img_rgb)
            if center1:
                circle1 = plt.Circle(center1, radius1, fill=False, color='red', linewidth=2)
                plt.gca().add_patch(circle1)
                plt.plot(center1[0], center1[1], 'ro', markersize=8, label='外圆圆心')
            if center2:
                circle2 = plt.Circle(center2, radius2, fill=False, color='blue', linewidth=2)
                plt.gca().add_patch(circle2)
                plt.plot(center2[0], center2[1], 'bo', markersize=8, label='内圆圆心')
            plt.title('原图与检测到的圆形')
            plt.legend()
            plt.axis('off')
            
            # 黑色掩码（外圆）
            plt.subplot(2, 3, 2)
            plt.imshow(mask_black, cmap='gray')
            plt.title('黑色区域掩码（外圆）')
            plt.axis('off')
            
            # 灰色掩码（内圆）
            plt.subplot(2, 3, 3)
            plt.imshow(mask_gray, cmap='gray')
            plt.title('灰色区域掩码（内圆）')
            plt.axis('off')
            
            # 放大显示圆心区域
            plt.subplot(2, 3, 4)
            # 计算显示区域
            if center1 and center2:
                min_x = max(0, min(center1[0], center2[0]) - 50)
                max_x = min(img_rgb.shape[1], max(center1[0], center2[0]) + 50)
                min_y = max(0, min(center1[1], center2[1]) - 50)
                max_y = min(img_rgb.shape[0], max(center1[1], center2[1]) + 50)
                
                zoom_img = img_rgb[min_y:max_y, min_x:max_x]
                plt.imshow(zoom_img)
                
                # 调整圆心坐标到放大图
                adj_center1 = (center1[0] - min_x, center1[1] - min_y)
                adj_center2 = (center2[0] - min_x, center2[1] - min_y)
                
                plt.plot(adj_center1[0], adj_center1[1], 'ro', markersize=10, label='外圆圆心')
                plt.plot(adj_center2[0], adj_center2[1], 'bo', markersize=10, label='内圆圆心')
                plt.plot([adj_center1[0], adj_center2[0]], [adj_center1[1], adj_center2[1]], 'g--', linewidth=2, label=f'距离: {distance:.1f}px')
                
                plt.title('圆心对齐详细视图')
                plt.legend()
                plt.axis('off')
            
            # 边缘检测
            plt.subplot(2, 3, 5)
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            plt.imshow(edges, cmap='gray')
            plt.title('边缘检测结果')
            plt.axis('off')
            
            # 对齐状态
            plt.subplot(2, 3, 6)
            plt.text(0.5, 0.7, '对齐状态', ha='center', va='center', fontsize=16, fontweight='bold', transform=plt.gca().transAxes)
            status_text = '✅ 已对齐' if distance <= alignment_threshold else '❌ 未对齐'
            plt.text(0.5, 0.4, status_text, ha='center', va='center', fontsize=20, fontweight='bold', 
                    color='green' if distance <= alignment_threshold else 'red', transform=plt.gca().transAxes)
            plt.text(0.5, 0.2, f'圆心距离: {distance:.2f}像素', ha='center', va='center', fontsize=12, transform=plt.gca().transAxes)
            plt.axis('off')
            
            plt.tight_layout()
            plt.savefig('circle_alignment_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            return True, distance, center1, center2
            
        else:
            print("未能检测到完整的内外圆结构")
            return False, None, None, None
            
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        return False, None, None, None

def pixel_wise_analysis(image_path):
    """像素级别的详细分析"""
    img = cv2.imread(image_path)
    if img is None:
        print("无法读取图片文件")
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 使用霍夫圆检测
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=50, param2=30, minRadius=10, maxRadius=200)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        
        print("\n=== 像素级别圆形检测 ===")
        print(f"检测到 {len(circles[0])} 个圆形")
        
        for i, circle in enumerate(circles[0]):
            x, y, r = circle
            print(f"圆形 {i+1}: 圆心=({x}, {y}), 半径={r}")
            
            # 分析该圆形区域的像素特征
            mask = np.zeros(gray.shape, np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1)
            
            # 计算圆形区域内的平均亮度
            mean_brightness = cv2.mean(gray, mask=mask)[0]
            print(f"  平均亮度: {mean_brightness:.1f}")
    
    return circles

if __name__ == "__main__":
    image_path = "截圆.png"
    
    print("开始分析圆形对齐情况...")
    
    # 主要分析
    success, distance, center1, center2 = analyze_circle_alignment(image_path)
    
    if success:
        print(f"\n分析完成！圆心距离: {distance:.2f} 像素")
    else:
        print("\n分析失败，尝试像素级别分析...")
        pixel_wise_analysis(image_path)