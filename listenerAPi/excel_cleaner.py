#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel数据清洗工具
用于处理影刀数据表格，提取指定列数据
"""

import pandas as pd
import numpy as np
import os
import json
from typing import List, Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class ExcelDataCleaner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.original_columns = []
        self.cleaned_data = None
        
    def load_excel(self, sheet_name: Optional[str] = None) -> bool:
        """加载Excel文件"""
        try:
            if sheet_name:
                self.df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            else:
                # 自动获取第一个工作表
                excel_file = pd.ExcelFile(self.file_path)
                first_sheet = excel_file.sheet_names[0]
                self.df = pd.read_excel(self.file_path, sheet_name=first_sheet)
                print(f"已加载工作表: {first_sheet}")
            
            self.original_columns = self.df.columns.tolist()
            print(f"原始列名: {self.original_columns}")
            return True
            
        except Exception as e:
            print(f"加载Excel文件失败: {e}")
            return False
    
    def analyze_columns(self) -> Dict[str, Any]:
        """分析列结构"""
        if self.df is None:
            return {}
        
        analysis = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'columns': [],
            'missing_values': {},
            'data_types': {}
        }
        
        for col in self.df.columns:
            col_info = {
                'name': col,
                'type': str(self.df[col].dtype),
                'non_null_count': self.df[col].count(),
                'null_count': self.df[col].isnull().sum(),
                'unique_values': self.df[col].nunique(),
                'sample_values': self.df[col].dropna().head(3).tolist()
            }
            analysis['columns'].append(col_info)
            analysis['missing_values'][col] = self.df[col].isnull().sum()
            analysis['data_types'][col] = str(self.df[col].dtype)
        
        return analysis
    
    def find_target_columns(self, target_names: List[str]) -> Dict[str, str]:
        """查找目标列名（支持模糊匹配）"""
        column_mapping = {}
        
        for target in target_names:
            target_lower = str(target).lower().strip()
            best_match = None
            best_score = 0
            
            for col in self.original_columns:
                col_lower = str(col).lower().strip()
                
                # 精确匹配
                if target_lower == col_lower:
                    best_match = col
                    best_score = 100
                    break
                
                # 包含匹配
                if target_lower in col_lower or col_lower in target_lower:
                    if len(col_lower) > best_score:
                        best_match = col
                        best_score = len(col_lower)
            
            if best_match:
                column_mapping[target] = best_match
                print(f"找到匹配: {target} -> {best_match}")
            else:
                print(f"未找到匹配: {target}")
        
        return column_mapping
    
    def clean_data(self, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """清洗数据"""
        if not column_mapping:
            print("没有有效的列映射")
            return pd.DataFrame()
        
        # 选择需要的列
        available_columns = [col for col in column_mapping.values() 
                          if col in self.df.columns]
        
        if not available_columns:
            print("没有可用的列")
            return pd.DataFrame()
        
        # 提取数据
        cleaned_df = self.df[available_columns].copy()
        
        # 重命名列
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        cleaned_df = cleaned_df.rename(columns=reverse_mapping)
        
        # 数据清洗
        for col in cleaned_df.columns:
            # 处理空值
            if cleaned_df[col].dtype in ['int64', 'float64']:
                cleaned_df[col] = cleaned_df[col].fillna(0)
            else:
                cleaned_df[col] = cleaned_df[col].fillna('')
            
            # 去除空白字符
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
        
        self.cleaned_data = cleaned_df
        return cleaned_df
    
    def export_data(self, output_path: str, format_type: str = 'excel') -> bool:
        """导出清洗后的数据"""
        if self.cleaned_data is None or self.cleaned_data.empty:
            print("没有数据可导出")
            return False
        
        try:
            if format_type.lower() == 'excel':
                self.cleaned_data.to_excel(output_path, index=False)
            elif format_type.lower() == 'csv':
                self.cleaned_data.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif format_type.lower() == 'json':
                self.cleaned_data.to_json(output_path, orient='records', force_ascii=False, indent=2)
            else:
                print(f"不支持的格式: {format_type}")
                return False
            
            print(f"数据已导出到: {output_path}")
            return True
            
        except Exception as e:
            print(f"导出数据失败: {e}")
            return False
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成数据摘要"""
        if self.cleaned_data is None or self.cleaned_data.empty:
            return {}
        
        summary = {
            'total_records': len(self.cleaned_data),
            'columns': list(self.cleaned_data.columns),
            'data_types': {},
            'sample_data': self.cleaned_data.head(10).to_dict('records'),
            'null_counts': {},
            'value_counts': {}
        }
        
        for col in self.cleaned_data.columns:
            summary['data_types'][col] = str(self.cleaned_data[col].dtype)
            summary['null_counts'][col] = self.cleaned_data[col].isnull().sum()
            
            # 分类统计
            if self.cleaned_data[col].dtype == 'object':
                value_counts = self.cleaned_data[col].value_counts()
                summary['value_counts'][col] = value_counts.head(10).to_dict()
            else:
                summary['value_counts'][col] = {
                    'mean': self.cleaned_data[col].mean() if self.cleaned_data[col].dtype in ['int64', 'float64'] else None,
                    'min': self.cleaned_data[col].min() if self.cleaned_data[col].dtype in ['int64', 'float64'] else None,
                    'max': self.cleaned_data[col].max() if self.cleaned_data[col].dtype in ['int64', 'float64'] else None
                }
        
        return summary

def main():
    """主函数"""
    # 目标文件路径
    excel_file = "影刀数据表格_20250916-143820.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"文件不存在: {excel_file}")
        return
    
    # 创建清洗器
    cleaner = ExcelDataCleaner(excel_file)
    
    # 加载Excel文件
    if not cleaner.load_excel():
        return
    
    print("=" * 50)
    print("Excel数据清洗工具")
    print("=" * 50)
    
    # 分析列结构
    analysis = cleaner.analyze_columns()
    print(f"\n数据概览:")
    print(f"总行数: {analysis['total_rows']}")
    print(f"总列数: {analysis['total_columns']}")
    
    # 显示列信息
    print("\n列信息:")
    for col in analysis['columns']:
        print(f"  {col['name']}: {col['type']} (空值: {col['null_count']}, 唯一值: {col['unique_values']})")
    
    # 查找目标列
    target_columns = ["货号", "已买", "精选", "想要"]
    column_mapping = cleaner.find_target_columns(target_columns)
    
    if not column_mapping:
        print("\n未找到目标列，请手动指定列名")
        print("可用列名:", cleaner.original_columns)
        return
    
    # 清洗数据
    cleaned_df = cleaner.clean_data(column_mapping)
    
    if cleaned_df.empty:
        print("数据清洗失败")
        return
    
    print(f"\n清洗结果:")
    print(f"成功提取 {len(cleaned_df)} 行数据")
    print(f"列名: {list(cleaned_df.columns)}")
    
    # 显示前10行数据
    print("\n前10行数据:")
    print(cleaned_df.head(10).to_string(index=False))
    
    # 导出数据
    output_file = "cleaned_data.xlsx"
    if cleaner.export_data(output_file):
        # 生成摘要
        summary = cleaner.generate_summary()
        summary_file = "data_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n数据摘要已保存到: {summary_file}")
        print(f"清洗后的数据已保存到: {output_file}")

if __name__ == "__main__":
    main()