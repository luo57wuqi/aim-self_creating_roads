#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影刀数据表格清洗工具 - 最终版
支持多种方式读取Excel数据
"""

import csv
import json
import os
import sys
from typing import List, Dict, Any

class ExcelDataCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.headers = []
        self.data = []
    
    def read_file(self) -> bool:
        """读取文件，尝试多种方法"""
        
        # 方法1: 尝试使用xlrd
        try:
            import xlrd
            print("检测到xlrd库，正在读取...")
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
            print(f"xlrd读取失败: {e}")
        
        # 方法2: 检查CSV文件
        csv_file = os.path.splitext(self.file_path)[0] + '.csv'
        if os.path.exists(csv_file):
            return self.read_csv(csv_file)
        
        # 方法3: 提示用户转换
        print("\n=== 转换指南 ===")
        print("请将Excel文件转换为CSV格式:")
        print("1. 用Excel打开文件")
        print("2. 点击 文件 -> 另存为")
        print("3. 选择CSV UTF-8格式")
        print("4. 保存为: 影刀数据表格_20250916-143820.csv")
        
        return False
    
    def read_csv(self, csv_path: str) -> bool:
        """读取CSV文件"""
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                self.headers = reader.fieldnames
                self.data = [row for row in reader]
            print(f"成功读取CSV文件，共{len(self.data)}行数据")
            return True
        except UnicodeDecodeError:
            try:
                with open(csv_path, 'r', encoding='gbk') as file:
                    reader = csv.DictReader(file)
                    self.headers = reader.fieldnames
                    self.data = [row for row in reader]
                print(f"成功读取CSV文件(GBK编码)，共{len(self.data)}行数据")
                return True
            except Exception as e:
                print(f"读取CSV文件失败: {e}")
                return False
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return False
    
    def find_target_columns(self, target_names: List[str]) -> Dict[str, str]:
        """查找目标列名"""
        column_mapping = {}
        
        for target in target_names:
            target_clean = str(target).strip()
            best_match = None
            best_score = 0
            
            for header in self.headers:
                header_clean = str(header).strip()
                
                # 精确匹配
                if target_clean == header_clean:
                    best_match = header
                    best_score = 100
                    break
                
                # 模糊匹配
                target_lower = target_clean.lower()
                header_lower = header_clean.lower()
                
                if target_lower == header_lower:
                    score = 90
                elif target_lower in header_lower:
                    score = 80
                elif header_lower in target_lower:
                    score = 70
                else:
                    continue
                
                if score > best_score:
                    best_match = header
                    best_score = score
            
            if best_match:
                column_mapping[target] = best_match
                print(f"✓ 找到匹配: {target} -> {best_match}")
            else:
                print(f"✗ 未找到: {target}")
        
        return column_mapping
    
    def extract_columns(self, column_mapping: Dict[str, str]) -> List[Dict[str, str]]:
        """提取指定列数据"""
        if not column_mapping:
            return []
        
        extracted = []
        for row in self.data:
            new_row = {}
            for target, source in column_mapping.items():
                value = row.get(source, '')
                if value is None:
                    value = ''
                else:
                    value = str(value).strip()
                new_row[target] = value
            extracted.append(new_row)
        
        return extracted
    
    def save_data(self, data: List[Dict[str, str]], base_name: str) -> None:
        """保存数据到多种格式"""
        if not data:
            print("没有数据可保存")
            return
        
        # CSV格式
        csv_file = f"{base_name}_清洗后.csv"
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"✓ CSV文件已保存: {csv_file}")
        except Exception as e:
            print(f"保存CSV失败: {e}")
        
        # JSON格式
        json_file = f"{base_name}_清洗后.json"
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON文件已保存: {json_file}")
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
            print(f"✓ TXT文件已保存: {txt_file}")
        except Exception as e:
            print(f"保存TXT失败: {e}")
    
    def generate_report(self, data: List[Dict[str, str]], mapping: Dict[str, str]) -> str:
        """生成清洗报告"""
        if not data:
            return "无数据"
        
        lines = []
        lines.append("=" * 50)
        lines.append("数据清洗报告")
        lines.append("=" * 50)
        lines.append(f"原始文件: {self.file_path}")
        lines.append(f"总记录数: {len(data)}")
        lines.append(f"提取列数: {len(mapping)}")
        lines.append("")
        
        lines.append("列映射:")
        for target, source in mapping.items():
            lines.append(f"  {target} <- {source}")
        lines.append("")
        
        # 数据统计
        for col in data[0].keys():
            non_empty = sum(1 for row in data if row.get(col, '').strip())
            lines.append(f"{col}: {non_empty}/{len(data)} 条记录有值")
        
        return "\n".join(lines)

def main():
    """主函数"""
    excel_file = "影刀数据表格_20250916-143820.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"错误: 文件 {excel_file} 不存在")
        return
    
    print("=" * 60)
    print("影刀数据表格清洗工具")
    print("=" * 60)
    print(f"处理文件: {excel_file}")
    
    cleaner = ExcelDataCleaner(excel_file)
    
    # 读取文件
    if not cleaner.read_file():
        return
    
    print(f"\n表头信息: {cleaner.headers}")
    
    # 查找目标列
    targets = ["货号", "已买", "精选", "想要"]
    mapping = cleaner.find_target_columns(targets)
    
    if not mapping:
        print("\n未找到目标列，请检查以下可用列名:")
        for i, header in enumerate(cleaner.headers, 1):
            print(f"{i}. {header}")
        return
    
    # 提取数据
    extracted = cleaner.extract_columns(mapping)
    
    if not extracted:
        print("数据提取失败")
        return
    
    # 保存数据
    base_name = os.path.splitext(excel_file)[0]
    cleaner.save_data(extracted, base_name)
    
    # 生成并保存报告
    report = cleaner.generate_report(extracted, mapping)
    report_file = f"{base_name}_清洗报告.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ 报告已保存: {report_file}")
    except Exception as e:
        print(f"保存报告失败: {e}")
    
    print("\n" + report)
    print("\n" + "=" * 60)
    print("清洗完成！请查看生成的文件")
    print("=" * 60)

if __name__ == "__main__":
    main()