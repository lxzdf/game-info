"""
数据清洗和预处理模块
"""

import pandas as pd
import numpy as np
import re
from tqdm import tqdm
import logging

class DataProcessor:
    """数据处理器 - 清洗和预处理玩家配置数据"""
    
    def __init__(self, data_path, chunk_size=10000):
        self.data_path = data_path
        self.chunk_size = chunk_size
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_processing.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def load_data(self):
        """加载数据 - 支持分块读取"""
        self.logger.info(f"加载数据: {self.data_path}")
        
        try:
            # 检查文件大小，决定是否分块
            file_size = os.path.getsize(self.data_path) / (1024 * 1024)  # MB
            self.logger.info(f"文件大小: {file_size:.2f} MB")
            
            if file_size > 100:  # 大于100MB时分块读取
                chunks = []
                total_rows = 0
                
                for chunk in tqdm(pd.read_csv(self.data_path, chunksize=self.chunk_size), 
                                desc="读取数据块"):
                    chunks.append(chunk)
                    total_rows += len(chunk)
                
                df = pd.concat(chunks, ignore_index=True)
                self.logger.info(f"分块读取完成，总行数: {total_rows}")
            else:
                df = pd.read_csv(self.data_path)
                self.logger.info(f"直接读取完成，总行数: {len(df)}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            raise
    
    def clean_data(self):
        """数据清洗主函数"""
        df = self.load_data()
        
        # 基本信息
        self.logger.info(f"原始数据形状: {df.shape}")
        self.logger.info(f"原始列名: {list(df.columns)}")
        
        # 重命名列（如果需要）
        column_mapping = {
            'cpu': 'CPU',
            'gpu': 'GPU', 
            'ram': 'RAM',
            'storage': 'Storage',
            'year': 'Year',
            'type': 'Type'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        # 1. 处理缺失值
        df_cleaned = self._handle_missing_values(df)
        
        # 2. 标准化格式
        df_cleaned = self._standardize_formats(df_cleaned)
        
        # 3. 清理异常值
        df_cleaned = self._remove_outliers(df_cleaned)
        
        # 4. 验证数据质量
        self._validate_data(df_cleaned)
        
        self.logger.info(f"清洗后数据形状: {df_cleaned.shape}")
        
        return df_cleaned
    
    def _handle_missing_values(self, df):
        """处理缺失值"""
        self.logger.info("处理缺失值...")
        
        # 统计缺失值
        missing_stats = df.isnull().sum()
        self.logger.info(f"缺失值统计:\n{missing_stats[missing_stats > 0]}")
        
        # 复制数据
        df_cleaned = df.copy()
        
        # 按列处理缺失值
        for column in df_cleaned.columns:
            if df_cleaned[column].isnull().sum() > 0:
                if column in ['CPU', 'GPU']:
                    # 关键列，用占位符填充
                    df_cleaned[column] = df_cleaned[column].fillna('Unknown')
                elif column in ['RAM', 'Storage']:
                    # 硬件列，用中位数或默认值填充
                    df_cleaned[column] = df_cleaned[column].fillna('8GB DDR4') if column == 'RAM' else df_cleaned[column].fillna('512GB NVMe SSD')
                elif column == 'Year':
                    # 年份列，用众数填充
                    mode_year = df_cleaned[column].mode()[0] if not df_cleaned[column].mode().empty else 2023
                    df_cleaned[column] = df_cleaned[column].fillna(mode_year)
                else:
                    # 其他列，向前填充
                    df_cleaned[column] = df_cleaned[column].ffill()
        
        return df_cleaned
    
    def _standardize_formats(self, df):
        """标准化数据格式"""
        self.logger.info("标准化数据格式...")
        
        df_cleaned = df.copy()
        
        # 1. 标准化CPU格式
        if 'CPU' in df_cleaned.columns:
            df_cleaned['CPU'] = df_cleaned['CPU'].apply(self._standardize_cpu_format)
        
        # 2. 标准化GPU格式
        if 'GPU' in df_cleaned.columns:
            df_cleaned['GPU'] = df_cleaned['GPU'].apply(self._standardize_gpu_format)
        
        # 3. 标准化RAM格式
        if 'RAM' in df_cleaned.columns:
            df_cleaned['RAM'] = df_cleaned['RAM'].apply(self._standardize_ram_format)
        
        # 4. 标准化Storage格式
        if 'Storage' in df_cleaned.columns:
            df_cleaned['Storage'] = df_cleaned['Storage'].apply(self._standardize_storage_format)
        
        # 5. 标准化Year为整数
        if 'Year' in df_cleaned.columns:
            df_cleaned['Year'] = pd.to_numeric(df_cleaned['Year'], errors='coerce').fillna(2023).astype(int)
        
        return df_cleaned
    
    def _standardize_cpu_format(self, cpu_str):
        """标准化CPU格式"""
        if pd.isna(cpu_str) or cpu_str == 'Unknown':
            return 'Unknown'
        
        cpu_str = str(cpu_str).strip().upper()
        
        # 确保Intel CPU以"Intel Core"开头
        if 'I9-' in cpu_str or 'I7-' in cpu_str or 'I5-' in cpu_str or 'I3-' in cpu_str:
            if not cpu_str.startswith('INTEL CORE'):
                cpu_str = 'Intel Core ' + cpu_str
        
        # 确保AMD CPU以"AMD Ryzen"开头
        elif 'RYZEN' in cpu_str and not cpu_str.startswith('AMD RYZEN'):
            cpu_str = 'AMD ' + cpu_str
        
        return cpu_str
    
    def _standardize_gpu_format(self, gpu_str):
        """标准化GPU格式"""
        if pd.isna(gpu_str) or gpu_str == 'Unknown':
            return 'Unknown'
        
        gpu_str = str(gpu_str).strip().upper()
        
        # 确保NVIDIA GPU以"NVIDIA GeForce"开头
        if ('RTX' in gpu_str or 'GTX' in gpu_str) and not gpu_str.startswith('NVIDIA'):
            if 'GEFORCE' not in gpu_str:
                gpu_str = 'NVIDIA GeForce ' + gpu_str
            else:
                gpu_str = 'NVIDIA ' + gpu_str
        
        # 确保AMD GPU以"AMD Radeon"开头
        elif ('RADEON' in gpu_str or 'RX' in gpu_str) and not gpu_str.startswith('AMD'):
            if 'RADEON' not in gpu_str:
                gpu_str = 'AMD Radeon ' + gpu_str
            else:
                gpu_str = 'AMD ' + gpu_str
        
        # 确保Intel GPU以"Intel Arc"开头
        elif 'ARC' in gpu_str and not gpu_str.startswith('INTEL'):
            gpu_str = 'Intel ' + gpu_str
        
        return gpu_str
    
    def _standardize_ram_format(self, ram_str):
        """标准化RAM格式"""
        if pd.isna(ram_str):
            return '8GB DDR4'
        
        ram_str = str(ram_str).strip().upper()
        
        # 确保有GB单位
        if 'GB' not in ram_str:
            # 尝试提取数字
            match = re.search(r'(\d+)', ram_str)
            if match:
                size = match.group(1)
                ram_str = f"{size}GB DDR4"
        
        # 确保有DDR类型
        if 'DDR' not in ram_str:
            ram_str += ' DDR4'
        
        return ram_str
    
    def _standardize_storage_format(self, storage_str):
        """标准化Storage格式"""
        if pd.isna(storage_str):
            return '512GB NVMe SSD'
        
        storage_str = str(storage_str).strip().upper()
        
        # 统一大小写和单位
        storage_str = storage_str.replace('TB', 'TB').replace('GB', 'GB')
        
        # 确保有存储类型
        if 'SSD' not in storage_str and 'HDD' not in storage_str and 'NVME' not in storage_str:
            storage_str += ' SSD'
        
        return storage_str
    
    def _remove_outliers(self, df):
        """移除异常值"""
        self.logger.info("检查异常值...")
        
        df_cleaned = df.copy()
        
        # 1. 检查Year异常值
        if 'Year' in df_cleaned.columns:
            # 移除2000年以前或2030年以后的异常年份
            valid_mask = (df_cleaned['Year'] >= 2000) & (df_cleaned['Year'] <= 2030)
            outliers = len(df_cleaned) - valid_mask.sum()
            if outliers > 0:
                self.logger.warning(f"发现异常年份: {outliers} 条")
                df_cleaned = df_cleaned[valid_mask].copy()
        
        # 2. 检查Type异常值
        if 'Type' in df_cleaned.columns:
            valid_types = ['Desktop', 'Laptop', 'Server', 'Unknown']
            invalid_mask = ~df_cleaned['Type'].isin(valid_types)
            outliers = invalid_mask.sum()
            if outliers > 0:
                self.logger.warning(f"发现异常类型: {outliers} 条")
                df_cleaned.loc[invalid_mask, 'Type'] = 'Unknown'
        
        return df_cleaned
    
    def _validate_data(self, df):
        """验证数据质量"""
        self.logger.info("验证数据质量...")
        
        validation_results = {
            '总行数': len(df),
            '总列数': len(df.columns),
            'CPU非空率': f"{df['CPU'].notnull().mean():.2%}",
            'GPU非空率': f"{df['GPU'].notnull().mean():.2%}",
            'RAM非空率': f"{df['RAM'].notnull().mean():.2%}",
            'Storage非空率': f"{df['Storage'].notnull().mean():.2%}",
            'Year范围': f"{df['Year'].min()} - {df['Year'].max()}",
            'Type分布': df['Type'].value_counts().to_dict()
        }
        
        for key, value in validation_results.items():
            self.logger.info(f"{key}: {value}")
        
        return validation_results

# 兼容性代码
import os
if not os.path.exists('logs'):
    os.makedirs('logs')