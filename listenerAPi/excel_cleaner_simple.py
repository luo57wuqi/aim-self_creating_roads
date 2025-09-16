#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据清洗工具 - 简化版
使用csv格式处理影刀数据表格
"""

import csv
import json
import os
import sys
from typing import List, Dict, Any

class SimpleDataCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.headers = []
        self.data = []
        
    def read_excel_as_csv(self) -> bool:
        """读取Excel文件（假设已转换为CSV）"""
        try:
            # 首先尝试直接读取Excel文件
            try:
                import xlrd
                workbook = xlrd.open_workbook(self.file_path)
                sheet = workbook.sheet_by_index(0)
                
                # 读取表头
                self.headers = [str(sheet.cell_value(0, col)) for col in range(sheet.ncols)]
                
                # 读取数据
                for row in range(1, sheet.nrows):
                    row_data = {}
                    for col in range(sheet.ncols):
                        value = sheet.cell_value(row, col)
                        if value is not None and str(value).strip():
                            row_data[self.headers[col]] = str(value).strip()
                        else:
                            row_data[self.headers[col]] = ''
                    self.data.append(row_data)
                
                print("使用xlrd成功读取Excel文件")
                return True
                
            except ImportError:
                print("xlrd未安装，尝试其他方法...")
                
            # 如果没有xlrd，提示用户转换格式
            print("请将Excel文件转换为CSV格式，或使用以下命令安装依赖：")
            print("pip install xlrd openpyxl")
            return False
            
        except Exception as e:
            print(f"读取文件失败: {e}")
            return False
    
    def read_csv_file(self, csv_path: str = None) -> bool:
        """读取CSV文件"""
        if csv_path is None:
            # 尝试查找同名的CSV文件
            base_name = os.path.splitext(self.file_path)[0]
            csv_path = base_name + '.csv'
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.headers = reader.fieldnames
                self.data = [row for row in reader]
            print(f"成功读取CSV文件: {csv_path}")
            return True
        except UnicodeDecodeError:
            try:
                with open(csv_path, 'r', encoding='gbk') as file:
                    reader = csv.DictReader(file)
                    self.headers = reader.fieldnames
                    self.data = [row for row in reader]
                print(f"成功读取CSV文件 (GBK编码): {csv_path}")
                return True
            except Exception as e:
                print(f"读取CSV文件失败: {e}")
                return False
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return False
    
    def find_columns(self, target_names: List[str]) -> Dict[str, str]:
        """查找目标列名"""
        column_mapping = {}
        
        for target in target_names:
            target_lower = str(target).lower().strip()
            best_match = None
            best_score = 0
            
            for header in self.headers:
                header_lower = str(header).lower().strip()
                
                # 精确匹配
                if target_lower == header_lower:
                    best_match = header
                    best_score = 100
                    break
                
                # 包含匹配
                if target_lower in header_lower or header_lower in target_lower:
                    score = max(len(target_lower), len(header_lower))
                    if score > best_score:
                        best_match = header
                        best_score = score
            
            if best_match:
                column_mapping[target] = best_match
                print(f"找到匹配: {target} -> {best_match}")
            else:
                print(f"未找到匹配: {target}")
        
        return column_mapping
    
    def extract_columns(self, column_mapping: Dict[str, str]) -> List[Dict[str, str]]:
        """提取指定列数据"""
        if not column_mapping:
            return []
        
        extracted_data = []
        
        for row in self.data:
            extracted_row = {}
            for target_col, source_col in column_mapping.items():
                if source_col in row:
                    value = row[source_col]
                    # 清理数据
                    if value is None:
                        value = ''
                    else:
                        value = str(value).strip()
                    extracted_row[target_col] = value
                else:
                    extracted_row[target_col] = ''
            extracted_data.append(extracted_row)
        
        return extracted_data
    
    def save_cleaned_data(self, data: List[Dict[str, str]], output_path: str, format_type: str = 'csv') -> bool:
        """保存清洗后的数据"""
        try:
            if not data:
                print("没有数据可保存")
                return False
            
            columns = list(data[0].keys())
            
            if format_type.lower() == 'csv':
                with open(output_path, 'w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.DictWriter(file, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(data)
                print(f"数据已保存到CSV文件: {output_path}")
            
            elif format_type.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                print(f"数据已保存到JSON文件: {output_path}")
            
            elif format_type.lower() == 'txt':
                with open(output_path, 'w', encoding='utf-8') as file:
                    # 制表符分隔
                    file.write('\t'.join(columns) + '\n')
                    for row in data:
                        values = [row.get(col, '') for col in columns]
                        file.write('\t'.join(values) + '\n')
                print(f"数据已保存到TXT文件: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
    
    def generate_report(self, data: List[Dict[str, str]], column_mapping: Dict[str, str]) -> str:
        """生成清洗报告"""
        if not data:
            return "没有数据"
        
        report = []
        report.append("=" * 50)
        report.append("数据清洗报告")
        report.append("=" * 50)
        report.append(f"原始文件: {self.file_path}")
        report.append(f"总记录数: {len(data)}")
        report.append(f"提取列数: {len(column_mapping)}")
        report.append("")
        
        report.append("列映射:")
        for target, source in column_mapping.items():
            report.append(f"  {target} <- {source}")
        report.append("")
        
        # 统计信息
        columns = list(data[0].keys())
        for col in columns:
            non_empty = sum(1 for row in data if row.get(col, '').strip())
            report.append(f"{col}: {non_empty}/{len(data)} 条记录有值")
        
        return "\n".join(report)

def convert_excel_to_csv(input_excel: str, output_csv: str = None) -> bool:
    """将Excel转换为CSV（需要用户手动转换）"""
    if output_csv is None:
        output_csv = os.path.splitext(input_excel)[0] + '.csv'
    
    print(f"请将 {input_excel} 转换为CSV格式")
    print(f"转换方法:")
    print(f"1. 用Excel打开文件")
    print(f"2. 点击 文件 -> 另存为")
    print(f"3. 选择CSV格式保存")
    print(f"4. 保存为: {output_csv}")
    return False

def main():
    """主函数"""
    excel_file = "影刀数据表格_20250916-143820.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"文件不存在: {excel_file}")
        return
    
    print("=" * 50)
    print("影刀数据表格清洗工具")
    print("=" * 50)
    
    cleaner = SimpleDataCleaner(excel_file)
    
    # 尝试读取文件
    success = False
    
    # 1. 尝试直接读取Excel
    if cleaner.read_excel_as_csv():
        success = True
    else:
        # 2. 尝试读取CSV文件
        csv_file = os.path.splitext(excel_file)[0] + '.csv'
        if os.path.exists(csv_file):
            if cleaner.read_csv_file(csv_file):
                success = True
        else:
            print(f"\n建议: 将Excel文件转换为CSV格式")
            convert_excel_to_csv(excel_file)
            return
    
    if not success:
        return
    
    print(f"\n文件读取成功!")
    print(f"表头: {cleaner.headers}")
    print(f"数据行数: {len(cleaner.data)}")
    
    # 查找目标列
    target_columns = ["货号", "已买", "精选", "想要"]
    column_mapping = cleaner.find_columns(target_columns)
    
    if not column_mapping:
        print("\n未找到目标列，请检查列名:")
        print("可用列名:", cleaner.headers)
        return
    
    # 提取数据
    extracted_data = cleaner.extract_columns(column_mapping)
    
    if not extracted_data:
        print("数据提取失败")
        return
    
    # 保存不同格式的文件
    base_name = os.path.splitext(excel_file)[0]
    
    # CSV格式
    csv_output = f"{base_name}_清洗后.csv"
    cleaner.save_cleaned_data(extracted_data, csv_output, 'csv')
    
    # JSON格式
    json_output = f"{base_name}_清洗后.json"
    cleaner.save_cleaned_data(extracted_data, json_output, 'json')
    
    # TXT格式
    txt_output = f"{base_name}_清洗后.txt"
    cleaner.save_cleaned_data(extracted_data, txt_output, 'txt')
    
    # 生成报告
    report = cleaner.generate_report(extracted_data, column_mapping)
    report_file = f"{base_name}_清洗报告.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{report}")
    print(f"\n所有文件已生成完成!")

if __name__ == "__main__":
    main()