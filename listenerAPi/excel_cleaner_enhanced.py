#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影刀数据表格清洗工具 - 增强版
支持智能列名匹配和模糊搜索
"""

import csv
import json
import os
import sys
from typing import List, Dict, Any

class EnhancedDataCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.headers = []
        self.data = []
    
    def read_file(self) -> bool:
        """读取文件"""
        # 优先尝试CSV文件
        csv_file = os.path.splitext(self.file_path)[0] + '.csv'
        if os.path.exists(csv_file):
            return self.read_csv(csv_file)
        
        # 尝试Excel文件
        try:
            import xlrd
            workbook = xlrd.open_workbook(self.file_path)
            sheet = workbook.sheet_by_index(0)
            
            self.headers = [str(sheet.cell_value(0, col)) for col in range(sheet.ncols)]
            
            for row in range(1, sheet.nrows):
                row_data = {}
                for col in range(sheet.ncols):
                    value = sheet.cell_value(row, col)
                    if value is None:
                        value = ''
                    else:
                        value = str(value).strip()
                    row_data[self.headers[col]] = value
                self.data.append(row_data)
            
            print(f"成功读取Excel文件，共{len(self.data)}行数据")
            return True
            
        except ImportError:
            print("xlrd库未安装，尝试CSV方式...")
        except Exception as e:
            print(f"读取Excel失败: {e}")
        
        return False
    
    def read_csv(self, csv_path: str) -> bool:
        """读取CSV文件"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'gb18030']
        
        for encoding in encodings:
            try:
                with open(csv_path, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    self.headers = reader.fieldnames
                    self.data = [row for row in reader]
                print(f"成功读取CSV文件({encoding}编码)，共{len(self.data)}行数据")
                return True
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"读取CSV文件失败: {e}")
                break
        
        return False
    
    def find_columns_intelligent(self, target_names: List[str]) -> Dict[str, str]:
        """智能查找目标列名"""
        column_mapping = {}
        
        # 定义别名映射
        alias_mapping = {
            "货号": ["货号", "商品货号", "编号", "产品编号", "商品编号"],
            "已买": ["已买", "已购买", "购买数量", "已购买数量", "购买", "销量"],
            "精选": ["精选", "精选标记", "是否精选", "推荐", "精选商品"],
            "想要": ["想要", "想要数量", "收藏", "关注", "需求"]
        }
        
        for target in target_names:
            found = False
            
            # 检查别名
            if target in alias_mapping:
                for alias in alias_mapping[target]:
                    for header in self.headers:
                        header_clean = str(header).strip()
                        if alias == header_clean:
                            column_mapping[target] = header
                            print(f"✓ 找到匹配: {target} -> {header}")
                            found = True
                            break
                    if found:
                        break
            
            if found:
                continue
            
            # 模糊匹配
            target_lower = str(target).lower()
            best_match = None
            best_score = 0
            
            for header in self.headers:
                header_lower = str(header).lower().strip()
                
                # 包含关系
                if target_lower in header_lower or header_lower in target_lower:
                    score = 85
                elif any(alias.lower() in header_lower for alias in alias_mapping.get(target, [])):
                    score = 80
                else:
                    score = 0
                
                if score > best_score:
                    best_match = header
                    best_score = score
            
            if best_match and best_score >= 60:
                column_mapping[target] = best_match
                print(f"✓ 模糊匹配: {target} -> {best_match}")
            else:
                print(f"✗ 未找到: {target}")
        
        return column_mapping
    
    def extract_and_clean(self, column_mapping: Dict[str, str]) -> List[Dict[str, str]]:
        """提取并清洗数据"""
        if not column_mapping:
            return []
        
        extracted = []
        for row in self.data:
            new_row = {}
            for target, source in column_mapping.items():
                value = row.get(source, '')
                
                # 数据清洗
                if value is None:
                    value = ''
                else:
                    value = str(value).strip()
                
                # 特殊处理
                if target == "已买" or target == "想要":
                    try:
                        value = str(int(float(value)))
                    except (ValueError, TypeError):
                        value = '0'
                
                elif target == "精选":
                    value_lower = value.lower()
                    if value_lower in ['是', '1', 'true', 'yes', 'y', '√']:
                        value = '是'
                    elif value_lower in ['否', '0', 'false', 'no', 'n', '×']:
                        value = '否'
                    else:
                        value = '否'
                
                new_row[target] = value
            extracted.append(new_row)
        
        return extracted
    
    def save_all_formats(self, data: List[Dict[str, str]], base_name: str) -> None:
        """保存所有格式"""
        if not data:
            print("没有数据可保存")
            return
        
        # CSV格式
        csv_file = f"{base_name}_完整清洗.csv"
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                for row in data:
                    clean_row = {col: row.get(col, '') for col in data[0].keys()}
                    writer.writerow(clean_row)
            print(f"✓ 完整CSV: {csv_file}")
        except Exception as e:
            print(f"保存CSV失败: {e}")
        
        # JSON格式
        json_file = f"{base_name}_清洗后.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON: {json_file}")
        except Exception as e:
            print(f"保存JSON失败: {e}")
        
        # TXT格式
        txt_file = f"{base_name}_清洗后.txt"
        try:
            with open(txt_file, 'w', encoding='utf-8') as f:
                headers = list(data[0].keys())
                f.write('\t'.join(headers) + '\n')
                for row in data:
                    values = [row.get(h, '') for h in headers]
                    f.write('\t'.join(values) + '\n')
            print(f"✓ TXT: {txt_file}")
        except Exception as e:
            print(f"保存TXT失败: {e}")
    
    def generate_detailed_report(self, data: List[Dict[str, str]], mapping: Dict[str, str]) -> str:
        """生成详细报告"""
        if not data:
            return "无数据"
        
        lines = []
        lines.append("=" * 60)
        lines.append("影刀数据表格清洗详细报告")
        lines.append("=" * 60)
        lines.append(f"原始文件: {self.file_path}")
        lines.append("")
        
        lines.append("📊 数据概览:")
        lines.append(f"  总记录数: {len(data)} 条")
        lines.append(f"  原始列数: {len(self.headers)} 个")
        lines.append(f"  提取列数: {len(mapping)} 个")
        lines.append("")
        
        lines.append("🎯 列映射详情:")
        for target, source in mapping.items():
            lines.append(f"  {target} ← {source}")
        lines.append("")
        
        lines.append("📈 数据统计:")
        for col in data[0].keys():
            values = [row.get(col, '') for row in data]
            non_empty = sum(1 for v in values if str(v).strip())
            
            if col in ["已买", "想要"]:
                try:
                    numbers = [int(v) for v in values if str(v).strip().isdigit()]
                    total = sum(numbers)
                    avg = total / len(numbers) if numbers else 0
                    lines.append(f"  {col}: {non_empty}条有值, 总计: {total}, 平均: {avg:.1f}")
                except:
                    lines.append(f"  {col}: {non_empty}/{len(data)} 条记录有值")
            elif col == "精选":
                yes_count = sum(1 for v in values if str(v) == '是')
                lines.append(f"  {col}: 是 {yes_count}条, 否 {len(data)-yes_count}条")
            else:
                lines.append(f"  {col}: {non_empty}/{len(data)} 条记录有值")
        
        return "\n".join(lines)

def main():
    """主函数"""
    excel_file = "影刀数据表格_20250916-143820.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"错误: 文件 {excel_file} 不存在")
        print("请确保文件在当前目录")
        return
    
    print("=" * 60)
    print("影刀数据表格智能清洗工具")
    print("=" * 60)
    print(f"处理文件: {excel_file}")
    
    cleaner = EnhancedDataCleaner(excel_file)
    
    # 读取文件
    if not cleaner.read_file():
        print("\n请先将Excel文件转换为CSV格式:")
        print("1. 用Excel打开文件")
        print("2. 文件 → 另存为")
        print("3. 选择 CSV UTF-8(逗号分隔)")
        print("4. 保存为: 影刀数据表格_20250916-143820.csv")
        return
    
    print(f"\n原始表头: {cleaner.headers}")
    
    # 智能查找目标列
    targets = ["货号", "已买", "精选", "想要"]
    mapping = cleaner.find_columns_intelligent(targets)
    
    if not mapping:
        print("\n❌ 未找到任何目标列")
        print("可用列名:")
        for i, header in enumerate(cleaner.headers, 1):
            print(f"  {i}. {header}")
        return
    
    # 提取并清洗数据
    extracted = cleaner.extract_and_clean(mapping)
    
    if not extracted:
        print("数据提取失败")
        return
    
    # 保存所有格式
    base_name = os.path.splitext(excel_file)[0]
    cleaner.save_all_formats(extracted, base_name)
    
    # 生成并保存详细报告
    report = cleaner.generate_detailed_report(extracted, mapping)
    report_file = f"{base_name}_详细报告.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ 详细报告: {report_file}")
    except Exception as e:
        print(f"保存报告失败: {e}")
    
    print("\n" + report)
    print("\n" + "=" * 60)
    print("✅ 清洗完成！请查看生成的文件")
    print("=" * 60)

if __name__ == "__main__":
    main()