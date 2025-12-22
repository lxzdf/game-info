#!/usr/bin/env python3
"""
玩家配置评分系统 - 主程序
处理5万条玩家配置数据，进行大数据清洗和评分计算
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from src.data_processor import DataProcessor
from src.fuzzy_matcher import FuzzyMatcher
from src.score_calculator import ScoreCalculator
import warnings
warnings.filterwarnings('ignore')

def setup_directories():
    """创建项目目录结构"""
    directories = ['data', 'configs', 'output', 'logs', 'src']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("📁 目录结构已创建")

def validate_files():
    """验证输入文件是否存在"""
    required_files = {
        'configs/CPU理论性能.xlsx': 'CPU评分表',
        'configs/显卡理论性能.xlsx': '显卡评分表',
        'configs/内存理论性能.xlsx': '内存评分表',
        'configs/硬盘理论性能.xlsx': '硬盘评分表',
        'data/player_pc_configs.csv': '玩家配置数据'
    }
    
    missing_files = []
    for file_path, desc in required_files.items():
        if not os.path.exists(file_path):
            missing_files.append(f"{desc}: {file_path}")
    
    if missing_files:
        print("❌ 缺少必要的文件:")
        for missing in missing_files:
            print(f"  - {missing}")
        return False
    
    print("✅ 所有必要文件已就绪")
    return True

def load_configs():
    """加载评分配置文件"""
    print("\n📊 加载评分配置文件...")
    
    try:
        # 加载CPU评分
        cpu_df = pd.read_excel('configs/CPU理论性能.xlsx')
        cpu_dict = dict(zip(cpu_df['CPU型号'], cpu_df['性能分']))
        
        # 加载显卡评分
        gpu_df = pd.read_excel('configs/显卡理论性能.xlsx')
        gpu_dict = dict(zip(gpu_df['显卡型号'], gpu_df['性能分']))
        
        # 加载内存评分
        ram_df = pd.read_excel('configs/内存理论性能.xlsx')
        ram_dict = dict(zip(ram_df['内存容量'], ram_df['性能分']))
        
        # 加载硬盘评分
        storage_df = pd.read_excel('configs/硬盘理论性能.xlsx')
        storage_dict = dict(zip(storage_df['硬盘容量'], storage_df['性能分']))
        
        print(f"✅ 加载完成: CPU({len(cpu_dict)}), GPU({len(gpu_dict)}), RAM({len(ram_dict)}), Storage({len(storage_dict)})")
        return cpu_dict, gpu_dict, ram_dict, storage_dict
        
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 玩家配置评分系统 v1.0")
    print("=" * 60)
    
    # 设置目录
    setup_directories()
    
    # 验证文件
    if not validate_files():
        sys.exit(1)
    
    # 加载配置文件
    cpu_dict, gpu_dict, ram_dict, storage_dict = load_configs()
    
    # 创建处理器实例
    print("\n🔄 初始化处理器...")
    data_processor = DataProcessor('data/player_pc_configs.csv')
    fuzzy_matcher = FuzzyMatcher(cpu_dict, gpu_dict)
    score_calculator = ScoreCalculator()
    
    # 处理数据
    print("\n🔧 开始数据处理...")
    
    # 1. 数据清洗
    print("步骤1: 数据清洗...")
    cleaned_df = data_processor.clean_data()
    
    # 2. 模糊匹配
    print("步骤2: 模糊匹配...")
    matched_df = fuzzy_matcher.match_all(cleaned_df)
    
    # 3. 计算评分
    print("步骤3: 计算评分...")
    scored_df = score_calculator.calculate_scores(matched_df, ram_dict, storage_dict)
    
    # 4. 添加性能等级
    print("步骤4: 添加性能等级...")
    scored_df = score_calculator.add_performance_level(scored_df)
    
    # 5. 保存结果
    print("步骤5: 保存结果...")
    
    # 保存为CSV
    csv_output = 'output/玩家配置评分数据.csv'
    scored_df.to_csv(csv_output, index=False, encoding='utf-8-sig')
    print(f"✅ CSV文件已保存: {csv_output}")
    
    # 保存为Excel
    excel_output = 'output/玩家配置评分数据.xlsx'
    scored_df.to_excel(excel_output, index=False)
    print(f"✅ Excel文件已保存: {excel_output}")
    
    # 6. 生成分析报告
    print("\n📈 生成分析报告...")
    report = score_calculator.generate_report(scored_df)
    print(report)
    
    # 7. 保存匹配统计
    print("\n📊 保存匹配统计...")
    stats = fuzzy_matcher.get_statistics()
    stats.to_csv('logs/matching_statistics.csv', index=False)
    print("✅ 匹配统计已保存到 logs/matching_statistics.csv")
    
    print("\n" + "=" * 60)
    print("🎉 处理完成！")
    print(f"📊 总记录数: {len(scored_df)}")
    print(f"📁 输出文件: output/玩家配置评分数据.[csv|xlsx]")
    print("=" * 60)

if __name__ == "__main__":
    main()