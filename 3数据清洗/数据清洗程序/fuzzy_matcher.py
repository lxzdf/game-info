"""
模糊匹配模块 - 处理CPU和GPU名称不完全匹配的情况
"""

import pandas as pd
import numpy as np
import re
import difflib
from collections import defaultdict
import jellyfish
from tqdm import tqdm

class FuzzyMatcher:
    """模糊匹配器 - 处理不完全匹配的硬件名称"""
    
    def __init__(self, cpu_dict, gpu_dict):
        self.cpu_dict = cpu_dict
        self.gpu_dict = gpu_dict
        self.cpu_cache = {}
        self.gpu_cache = {}
        
        # 统计信息
        self.stats = defaultdict(int)
        
        # 构建简化名称映射
        self._build_simplified_mappings()
    
    def _build_simplified_mappings(self):
        """构建简化名称映射"""
        # CPU简化映射
        self.cpu_simplified = {}
        for full_name in self.cpu_dict.keys():
            simplified = self._simplify_cpu_name(full_name)
            if simplified not in self.cpu_simplified:
                self.cpu_simplified[simplified] = []
            self.cpu_simplified[simplified].append(full_name)
        
        # GPU简化映射
        self.gpu_simplified = {}
        for full_name in self.gpu_dict.keys():
            simplified = self._simplify_gpu_name(full_name)
            if simplified not in self.gpu_simplified:
                self.gpu_simplified[simplified] = []
            self.gpu_simplified[simplified].append(full_name)
    
    def _simplify_cpu_name(self, cpu_name):
        """简化CPU名称"""
        cpu_name = str(cpu_name).upper()
        
        # 提取核心型号
        patterns = [
            r'I[3-9]-\d{4,5}[A-Z]*',  # I5-13600K
            r'RYZEN\s+[3-9]\s+\d{4,5}[A-Z]*',  # RYZEN 7 7700X
            r'CORE\s+ULTRA\s+\d+',  # CORE ULTRA 9
            r'THREADRIPPER\s+\d{4}',  # THREADRIPPER 9980X
        ]
        
        for pattern in patterns:
            match = re.search(pattern, cpu_name)
            if match:
                return match.group(0)
        
        # 如果未匹配到模式，返回原始名称的简化版
        return re.sub(r'\s+', ' ', cpu_name).strip()
    
    def _simplify_gpu_name(self, gpu_name):
        """简化GPU名称"""
        gpu_name = str(gpu_name).upper()
        
        # 提取显卡型号
        patterns = [
            r'RTX\s*\d{4,5}[A-Z\s]*',  # RTX 4060 Ti
            r'GTX\s*\d{4,5}[A-Z\s]*',  # GTX 1660 SUPER
            r'RX\s*\d{4,5}[A-Z\s]*',  # RX 6600 XT
            r'ARC\s*[A-Z]\d{3}',  # ARC A580
            r'GEFORCE\s*RTX\s*\d{4,5}[A-Z\s]*',
            r'RADEON\s*RX\s*\d{4,5}[A-Z\s]*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, gpu_name)
            if match:
                return re.sub(r'\s+', ' ', match.group(0)).strip()
        
        return re.sub(r'\s+', ' ', gpu_name).strip()
    
    def match_all(self, df):
        """为DataFrame中的所有行进行匹配"""
        print("🔄 开始模糊匹配...")
        
        # 创建结果DataFrame
        result_df = df.copy()
        
        # 匹配CPU
        print("匹配CPU...")
        cpu_scores = []
        cpu_matches = []
        
        for cpu in tqdm(df['CPU'], desc="CPU匹配"):
            score, match = self.match_cpu(cpu)
            cpu_scores.append(score)
            cpu_matches.append(match)
        
        result_df['CPU_Score'] = cpu_scores
        result_df['CPU_Match'] = cpu_matches
        
        # 匹配GPU
        print("匹配GPU...")
        gpu_scores = []
        gpu_matches = []
        
        for gpu in tqdm(df['GPU'], desc="GPU匹配"):
            score, match = self.match_gpu(gpu)
            gpu_scores.append(score)
            gpu_matches.append(match)
        
        result_df['GPU_Score'] = gpu_scores
        result_df['GPU_Match'] = gpu_matches
        
        # 更新统计
        self.stats['total_rows'] = len(df)
        self.stats['cpu_exact_match'] = (result_df['CPU_Match'] == result_df['CPU']).sum()
        self.stats['cpu_fuzzy_match'] = ((result_df['CPU_Match'] != result_df['CPU']) & 
                                        (result_df['CPU_Match'] != 'Unknown')).sum()
        self.stats['cpu_no_match'] = (result_df['CPU_Match'] == 'Unknown').sum()
        
        self.stats['gpu_exact_match'] = (result_df['GPU_Match'] == result_df['GPU']).sum()
        self.stats['gpu_fuzzy_match'] = ((result_df['GPU_Match'] != result_df['GPU']) & 
                                        (result_df['GPU_Match'] != 'Unknown')).sum()
        self.stats['gpu_no_match'] = (result_df['GPU_Match'] == 'Unknown').sum()
        
        return result_df
    
    def match_cpu(self, query):
        """匹配CPU型号"""
        if pd.isna(query) or query == 'Unknown':
            self.stats['cpu_unknown'] += 1
            return 0, 'Unknown'
        
        query_str = str(query).strip()
        
        # 检查缓存
        if query_str in self.cpu_cache:
            self.stats['cpu_cache_hit'] += 1
            return self.cpu_cache[query_str]
        
        # 1. 精确匹配
        if query_str in self.cpu_dict:
            self.stats['cpu_exact'] += 1
            result = (self.cpu_dict[query_str], query_str)
            self.cpu_cache[query_str] = result
            return result
        
        # 2. 简化匹配
        simplified_query = self._simplify_cpu_name(query_str)
        
        if simplified_query in self.cpu_simplified:
            candidates = self.cpu_simplified[simplified_query]
            if len(candidates) == 1:
                self.stats['cpu_simplified_exact'] += 1
                result = (self.cpu_dict[candidates[0]], candidates[0])
                self.cpu_cache[query_str] = result
                return result
            
            # 多个候选项，选择最相似的
            best_match = self._find_best_match(query_str, candidates)
            self.stats['cpu_simplified_fuzzy'] += 1
            result = (self.cpu_dict[best_match], best_match)
            self.cpu_cache[query_str] = result
            return result
        
        # 3. 模糊匹配
        best_match = self._fuzzy_match_cpu(query_str)
        if best_match:
            self.stats['cpu_fuzzy'] += 1
            result = (self.cpu_dict[best_match], best_match)
            self.cpu_cache[query_str] = result
            return result
        
        # 4. 默认分数
        self.stats['cpu_default'] += 1
        default_score = self._get_default_cpu_score(query_str)
        result = (default_score, f"Default: {query_str}")
        self.cpu_cache[query_str] = result
        return result
    
    def match_gpu(self, query):
        """匹配GPU型号"""
        if pd.isna(query) or query == 'Unknown':
            self.stats['gpu_unknown'] += 1
            return 0, 'Unknown'
        
        query_str = str(query).strip()
        
        # 检查缓存
        if query_str in self.gpu_cache:
            self.stats['gpu_cache_hit'] += 1
            return self.gpu_cache[query_str]
        
        # 1. 精确匹配
        if query_str in self.gpu_dict:
            self.stats['gpu_exact'] += 1
            result = (self.gpu_dict[query_str], query_str)
            self.gpu_cache[query_str] = result
            return result
        
        # 2. 简化匹配
        simplified_query = self._simplify_gpu_name(query_str)
        
        if simplified_query in self.gpu_simplified:
            candidates = self.gpu_simplified[simplified_query]
            if len(candidates) == 1:
                self.stats['gpu_simplified_exact'] += 1
                result = (self.gpu_dict[candidates[0]], candidates[0])
                self.gpu_cache[query_str] = result
                return result
            
            # 多个候选项，选择最相似的
            best_match = self._find_best_match(query_str, candidates)
            self.stats['gpu_simplified_fuzzy'] += 1
            result = (self.gpu_dict[best_match], best_match)
            self.gpu_cache[query_str] = result
            return result
        
        # 3. 模糊匹配
        best_match = self._fuzzy_match_gpu(query_str)
        if best_match:
            self.stats['gpu_fuzzy'] += 1
            result = (self.gpu_dict[best_match], best_match)
            self.gpu_cache[query_str] = result
            return result
        
        # 4. 默认分数
        self.stats['gpu_default'] += 1
        default_score = self._get_default_gpu_score(query_str)
        result = (default_score, f"Default: {query_str}")
        self.gpu_cache[query_str] = result
        return result
    
    def _find_best_match(self, query, candidates):
        """在候选项中寻找最佳匹配"""
        best_score = 0
        best_match = None
        
        for candidate in candidates:
            # 使用序列相似度
            similarity = difflib.SequenceMatcher(None, query.lower(), candidate.lower()).ratio()
            
            # 使用Jaro-Winkler距离（对前缀更敏感）
            jw_score = jellyfish.jaro_winkler_similarity(query.lower(), candidate.lower())
            
            # 综合得分
            combined_score = similarity * 0.5 + jw_score * 0.5
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = candidate
        
        return best_match if best_score > 0.6 else None
    
    def _fuzzy_match_cpu(self, query):
        """模糊匹配CPU"""
        # 在全部CPU名称中查找相似项
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for cpu_name in self.cpu_dict.keys():
            # 检查是否为同一系列
            is_same_series = False
            
            # Intel Core系列
            if ('intel' in query_lower and 'intel' in cpu_name.lower()) or \
               ('amd' in query_lower and 'amd' in cpu_name.lower()):
                
                # 检查代数（如i5-13xxx vs i5-14xxx）
                query_gen = re.search(r'i[3-9]-(\d{2})', query_lower)
                cpu_gen = re.search(r'i[3-9]-(\d{2})', cpu_name.lower())
                
                if query_gen and cpu_gen:
                    # 同一代CPU
                    if query_gen.group(1) == cpu_gen.group(1):
                        is_same_series = True
            
            # 计算相似度
            similarity = difflib.SequenceMatcher(None, query_lower, cpu_name.lower()).ratio()
            
            # 如果是同一系列，提高权重
            if is_same_series:
                similarity *= 1.2
            
            if similarity > best_score:
                best_score = similarity
                best_match = cpu_name
        
        return best_match if best_score > 0.7 else None
    
    def _fuzzy_match_gpu(self, query):
        """模糊匹配GPU"""
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for gpu_name in self.gpu_dict.keys():
            # 检查是否为同一品牌和系列
            is_same_series = False
            
            # 检查RTX/GTX系列
            query_series = re.search(r'(rtx|gtx|rx)\s*(\d{4})', query_lower)
            gpu_series = re.search(r'(rtx|gtx|rx)\s*(\d{4})', gpu_name.lower())
            
            if query_series and gpu_series:
                # 同一系列（如RTX 4060 vs RTX 4070）
                if query_series.group(1) == gpu_series.group(1):
                    is_same_series = True
            
            # 计算相似度
            similarity = difflib.SequenceMatcher(None, query_lower, gpu_name.lower()).ratio()
            
            # 如果是同一系列，提高权重
            if is_same_series:
                similarity *= 1.2
            
            if similarity > best_score:
                best_score = similarity
                best_match = gpu_name
        
        return best_match if best_score > 0.7 else None
    
    def _get_default_cpu_score(self, cpu_name):
        """获取默认CPU分数"""
        cpu_name = cpu_name.lower()
        
        if 'i9' in cpu_name or 'ryzen 9' in cpu_name or 'threadripper' in cpu_name:
            return 75
        elif 'i7' in cpu_name or 'ryzen 7' in cpu_name:
            return 65
        elif 'i5' in cpu_name or 'ryzen 5' in cpu_name:
            return 55
        elif 'i3' in cpu_name or 'ryzen 3' in cpu_name:
            return 40
        elif 'pentium' in cpu_name or 'athlon' in cpu_name:
            return 25
        else:
            return 30
    
    def _get_default_gpu_score(self, gpu_name):
        """获取默认GPU分数"""
        gpu_name = gpu_name.lower()
        
        # RTX 40系列
        if 'rtx 4090' in gpu_name:
            return 88
        elif 'rtx 4080' in gpu_name:
            return 80
        elif 'rtx 4070' in gpu_name:
            return 65
        elif 'rtx 4060' in gpu_name:
            return 50
        
        # RTX 30系列
        elif 'rtx 3090' in gpu_name:
            return 85
        elif 'rtx 3080' in gpu_name:
            return 75
        elif 'rtx 3070' in gpu_name:
            return 60
        elif 'rtx 3060' in gpu_name:
            return 45
        
        # GTX系列
        elif 'gtx 1660' in gpu_name:
            return 35
        elif 'gtx 1650' in gpu_name:
            return 30
        elif 'gtx 1060' in gpu_name:
            return 25
        
        # AMD系列
        elif 'rx 7900' in gpu_name:
            return 80
        elif 'rx 7800' in gpu_name:
            return 65
        elif 'rx 7700' in gpu_name:
            return 55
        elif 'rx 7600' in gpu_name:
            return 45
        elif 'rx 6600' in gpu_name:
            return 40
        
        # 集成显卡
        elif 'intel' in gpu_name and ('uhd' in gpu_name or 'iris' in gpu_name):
            return 15
        elif 'radeon' in gpu_name and ('vega' in gpu_name):
            return 20
        
        else:
            return 25
    
    def get_statistics(self):
        """获取匹配统计"""
        stats_df = pd.DataFrame([{
            '匹配类型': 'CPU精确匹配',
            '数量': self.stats['cpu_exact'],
            '百分比': f"{self.stats['cpu_exact']/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'CPU简化匹配',
            '数量': self.stats['cpu_simplified_exact'] + self.stats['cpu_simplified_fuzzy'],
            '百分比': f"{(self.stats['cpu_simplified_exact'] + self.stats['cpu_simplified_fuzzy'])/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'CPU模糊匹配',
            '数量': self.stats['cpu_fuzzy'],
            '百分比': f"{self.stats['cpu_fuzzy']/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'CPU默认分数',
            '数量': self.stats['cpu_default'],
            '百分比': f"{self.stats['cpu_default']/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'GPU精确匹配',
            '数量': self.stats['gpu_exact'],
            '百分比': f"{self.stats['gpu_exact']/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'GPU简化匹配',
            '数量': self.stats['gpu_simplified_exact'] + self.stats['gpu_simplified_fuzzy'],
            '百分比': f"{(self.stats['gpu_simplified_exact'] + self.stats['gpu_simplified_fuzzy'])/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'GPU模糊匹配',
            '数量': self.stats['gpu_fuzzy'],
            '百分比': f"{self.stats['gpu_fuzzy']/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }, {
            '匹配类型': 'GPU默认分数',
            '数量': self.stats['gpu_default'],
            '百分比': f"{self.stats['gpu_default']/self.stats['total_rows']:.2%}" if self.stats['total_rows'] > 0 else '0%'
        }])
        
        return stats_df