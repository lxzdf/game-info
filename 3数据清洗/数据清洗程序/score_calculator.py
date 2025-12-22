"""
评分计算模块 - 计算各项分数和总分
"""

import pandas as pd
import numpy as np
import re
from tqdm import tqdm

class ScoreCalculator:
    """评分计算器 - 计算硬件配置总分"""
    
    def __init__(self):
        self.weights = {
            'GPU': 0.4,    # 显卡权重 40%
            'CPU': 0.3,    # CPU权重 30%
            'RAM': 0.2,    # 内存权重 20%
            'Storage': 0.1  # 硬盘权重 10%
        }
    
    def calculate_scores(self, df, ram_dict, storage_dict):
        """计算所有评分"""
        print("🧮 计算各项评分...")
        
        result_df = df.copy()
        
        # 1. 计算RAM分数
        print("计算RAM分数...")
        result_df['RAM_Score'] = result_df['RAM'].progress_apply(
            lambda x: self._calculate_ram_score(x, ram_dict)
        )
        
        # 2. 计算Storage分数
        print("计算Storage分数...")
        result_df['Storage_Score'] = result_df['Storage'].progress_apply(
            lambda x: self._calculate_storage_score(x, storage_dict)
        )
        
        # 3. 计算总分（使用已匹配的CPU_Score和GPU_Score）
        print("计算总分...")
        result_df['Total_Score'] = (
            self.weights['GPU'] * result_df['GPU_Score'] +
            self.weights['CPU'] * result_df['CPU_Score'] +
            self.weights['RAM'] * result_df['RAM_Score'] +
            self.weights['Storage'] * result_df['Storage_Score']
        ).round(2)
        
        # 4. 移除临时匹配列
        if 'CPU_Match' in result_df.columns:
            result_df.drop(columns=['CPU_Match'], inplace=True)
        if 'GPU_Match' in result_df.columns:
            result_df.drop(columns=['GPU_Match'], inplace=True)
        
        return result_df
    
    def _calculate_ram_score(self, ram_str, ram_dict):
        """计算RAM分数"""
        if pd.isna(ram_str):
            return 0
        
        ram_str = str(ram_str).upper()
        
        # 尝试精确匹配
        for ram_key in ram_dict.keys():
            if ram_key.upper() in ram_str:
                return ram_dict[ram_key]
        
        # 提取容量并匹配
        match = re.search(r'(\d+)GB', ram_str)
        if match:
            gb = int(match.group(1))
            
            # 根据容量范围分配分数
            if gb >= 64:
                return 100
            elif gb >= 48:
                return 90
            elif gb >= 32:
                return 80
            elif gb >= 24:
                return 70
            elif gb >= 16:
                return 60
            elif gb >= 8:
                return 20
            elif gb >= 4:
                return 10
        
        return 0
    
    def _calculate_storage_score(self, storage_str, storage_dict):
        """计算Storage分数"""
        if pd.isna(storage_str):
            return 0
        
        storage_str = str(storage_str).upper()
        
        # 处理多个存储设备的情况（如 "512GB SSD + 1TB HDD"）
        if '+' in storage_str:
            # 取最大的存储设备
            parts = storage_str.split('+')
            scores = []
            for part in parts:
                score = self._get_single_storage_score(part.strip(), storage_dict)
                scores.append(score)
            return max(scores) if scores else 0
        
        return self._get_single_storage_score(storage_str, storage_dict)
    
    def _get_single_storage_score(self, storage_str, storage_dict):
        """获取单个存储设备的分数"""
        # 尝试精确匹配
        for storage_key in storage_dict.keys():
            if storage_key.upper() in storage_str:
                return storage_dict[storage_key]
        
        # 基于容量和类型推断
        storage_lower = storage_str.lower()
        
        # 检查容量
        capacity_score = 0
        if '4tb' in storage_lower or '4t' in storage_lower:
            capacity_score = 100
        elif '2tb' in storage_lower or '2t' in storage_lower:
            capacity_score = 90
        elif '1tb' in storage_lower or '1t' in storage_lower:
            capacity_score = 60
        elif '512gb' in storage_lower or '512g' in storage_lower:
            capacity_score = 30
        elif '256gb' in storage_lower or '256g' in storage_lower:
            capacity_score = 20
        elif '128gb' in storage_lower or '128g' in storage_lower:
            capacity_score = 10
        
        # 检查存储类型
        type_multiplier = 1.0
        if 'nvme' in storage_lower or 'pcie' in storage_lower:
            type_multiplier = 1.2  # NVMe SSD性能更好
        elif 'ssd' in storage_lower:
            type_multiplier = 1.0  # 普通SSD
        elif 'hdd' in storage_lower:
            type_multiplier = 0.6  # HDD性能较差
        
        return int(capacity_score * type_multiplier)
    
    def add_performance_level(self, df):
        """添加性能等级"""
        print("🏷️ 添加性能等级...")
        
        def get_performance_level(score):
            if score >= 90:
                return '顶级'
            elif score >= 80:
                return '高端'
            elif score >= 70:
                return '中高端'
            elif score >= 60:
                return '中端'
            elif score >= 50:
                return '入门级'
            else:
                return '基础级'
        
        df['Performance_Level'] = df['Total_Score'].apply(get_performance_level)
        return df
    
    def generate_report(self, df):
        """生成分析报告"""
        print("📊 生成分析报告...")
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📈 玩家配置评分分析报告")
        report_lines.append("=" * 60)
        
        # 基础统计
        report_lines.append(f"\n📊 基础统计")
        report_lines.append(f"总记录数: {len(df):,}")
        report_lines.append(f"数据年份范围: {df['Year'].min()} - {df['Year'].max()}")
        
        # 设备类型分布
        if 'Type' in df.columns:
            type_dist = df['Type'].value_counts()
            report_lines.append(f"\n💻 设备类型分布:")
            for type_name, count in type_dist.items():
                report_lines.append(f"  {type_name}: {count:,} ({count/len(df):.1%})")
        
        # 评分统计
        report_lines.append(f"\n🎯 评分统计:")
        for score_col in ['CPU_Score', 'GPU_Score', 'RAM_Score', 'Storage_Score', 'Total_Score']:
            if score_col in df.columns:
                report_lines.append(f"\n{score_col}:")
                report_lines.append(f"  平均值: {df[score_col].mean():.2f}")
                report_lines.append(f"  中位数: {df[score_col].median():.2f}")
                report_lines.append(f"  最大值: {df[score_col].max():.2f}")
                report_lines.append(f"  最小值: {df[score_col].min():.2f}")
                report_lines.append(f"  标准差: {df[score_col].std():.2f}")
        
        # 性能等级分布
        if 'Performance_Level' in df.columns:
            report_lines.append(f"\n🏆 性能等级分布:")
            level_dist = df['Performance_Level'].value_counts().sort_index()
            for level, count in level_dist.items():
                report_lines.append(f"  {level}: {count:,} ({count/len(df):.1%})")
        
        # 高分配置（前10）
        report_lines.append(f"\n⭐ 最高分配置（前10）:")
        top_configs = df.nlargest(10, 'Total_Score')[['ID', 'CPU', 'GPU', 'RAM', 'Storage', 'Total_Score']]
        for _, row in top_configs.iterrows():
            report_lines.append(f"  ID {row['ID']}: {row['Total_Score']:.2f}分")
            report_lines.append(f"    CPU: {row['CPU']}")
            report_lines.append(f"    GPU: {row['GPU']}")
            report_lines.append(f"    RAM: {row['RAM']}, Storage: {row['Storage']}")
        
        # 各年性能趋势
        if 'Year' in df.columns:
            report_lines.append(f"\n📅 按年份性能趋势:")
            yearly_avg = df.groupby('Year')['Total_Score'].mean().round(2)
            for year, avg_score in yearly_avg.items():
                report_lines.append(f"  {year}年: 平均{avg_score}分")
        
        # 相关性分析
        report_lines.append(f"\n🔗 相关性分析:")
        score_columns = ['CPU_Score', 'GPU_Score', 'RAM_Score', 'Storage_Score']
        correlation_matrix = df[score_columns].corr()
        
        for i, col1 in enumerate(score_columns):
            for j, col2 in enumerate(score_columns):
                if i < j:
                    corr = correlation_matrix.loc[col1, col2]
                    report_lines.append(f"  {col1} vs {col2}: {corr:.3f}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def save_detailed_analysis(self, df, output_path='output/详细分析报告.txt'):
        """保存详细分析报告"""
        report = self.generate_report(df)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 详细分析报告已保存: {output_path}")
        return report