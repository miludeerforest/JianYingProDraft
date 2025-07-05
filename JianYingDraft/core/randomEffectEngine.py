"""
 * @file   : randomEffectEngine.py
 * @time   : 20:15
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from JianYingDraft.core.metadataManager import MetadataManager
from JianYingDraft.core.configManager import AutoMixConfigManager


class RandomEffectEngine:
    """
    随机效果引擎
    基于元数据管理器实现智能的随机特效、滤镜、转场选择和参数调整
    """
    
    def __init__(self, metadata_manager: MetadataManager, config_manager: AutoMixConfigManager = None):
        """
        初始化随机效果引擎
        
        Args:
            metadata_manager: 元数据管理器实例
            config_manager: 配置管理器实例
        """
        self.metadata_manager = metadata_manager
        self.config_manager = config_manager or AutoMixConfigManager
        
        # 效果使用历史，用于避免重复
        self.used_filters: Set[str] = set()
        self.used_transitions: Set[str] = set()
        self.used_effects: Set[str] = set()
        
        # 效果权重配置
        self.filter_weights = {}
        self.transition_weights = {}
        self.effect_weights = {}
        
        # 初始化权重
        self._initialize_weights()
    
    def _initialize_weights(self):
        """初始化效果权重"""
        # 获取所有可用效果
        use_vip = self.config_manager.get_use_vip_effects()
        
        filters = self.metadata_manager.get_available_filters(vip_only=use_vip, free_only=not use_vip)
        transitions = self.metadata_manager.get_available_transitions(vip_only=use_vip, free_only=not use_vip)
        effects = self.metadata_manager.get_available_effects(vip_only=use_vip, free_only=not use_vip)
        
        # 为每个效果设置默认权重
        for filter_meta in filters:
            name = getattr(filter_meta, 'name', '')
            self.filter_weights[name] = 1.0
        
        for transition_meta in transitions:
            name = getattr(transition_meta, 'name', '')
            self.transition_weights[name] = 1.0
        
        for effect_meta in effects:
            name = getattr(effect_meta, 'name', '')
            self.effect_weights[name] = 1.0
    
    def select_filter_for_segment(self, segment_info: Dict[str, Any]) -> Optional[Any]:
        """
        为视频片段选择合适的滤镜
        
        Args:
            segment_info: 视频片段信息
            
        Returns:
            Optional[Any]: 选择的滤镜元数据，如果不应用滤镜则返回None
        """
        # 获取可用滤镜（使用VIP资源，100%概率确保每个片段都有滤镜）
        available_filters = self.metadata_manager.get_available_filters()
        
        if not available_filters:
            return None
        
        # 应用多样性策略
        diverse_filters = self._ensure_filter_diversity(available_filters)
        
        if not diverse_filters:
            # 如果所有滤镜都用过了，重置历史
            self.used_filters.clear()
            diverse_filters = available_filters
        
        # 基于权重选择滤镜
        selected_filter = self._weighted_random_choice(
            diverse_filters, 
            self.filter_weights
        )
        
        if selected_filter:
            filter_name = getattr(selected_filter, 'name', '')
            self.used_filters.add(filter_name)
        
        return selected_filter
    
    def select_transition_between_segments(self, prev_segment: Dict[str, Any], 
                                         next_segment: Dict[str, Any]) -> Optional[Tuple[Any, int]]:
        """
        为两个片段间选择转场
        
        Args:
            prev_segment: 前一个片段信息
            next_segment: 下一个片段信息
            
        Returns:
            Optional[Tuple[Any, int]]: (转场元数据, 转场时长微秒)，如果不应用转场则返回None
        """
        # 检查是否应该应用转场
        transition_probability = self.config_manager.get_transition_probability()
        if random.random() > transition_probability:
            return None
        
        # 获取可用转场（使用VIP资源）
        all_transitions = self.metadata_manager.get_available_transitions()

        # 过滤掉弹幕类转场特效
        available_transitions = self._filter_transitions(all_transitions)
        
        if not available_transitions:
            return None
        
        # 应用多样性策略
        diverse_transitions = self._ensure_transition_diversity(available_transitions)
        
        if not diverse_transitions:
            # 如果所有转场都用过了，重置历史
            self.used_transitions.clear()
            diverse_transitions = available_transitions
        
        # 基于权重选择转场
        selected_transition = self._weighted_random_choice(
            diverse_transitions, 
            self.transition_weights
        )
        
        if selected_transition:
            transition_name = getattr(selected_transition, 'name', '')
            self.used_transitions.add(transition_name)
            
            # 计算转场时长
            duration = self._calculate_transition_duration(selected_transition, prev_segment, next_segment)
            
            return selected_transition, duration
        
        return None
    
    def select_effect_for_segment(self, segment_info: Dict[str, Any]) -> Optional[Any]:
        """
        为视频片段选择特效
        
        Args:
            segment_info: 视频片段信息
            
        Returns:
            Optional[Any]: 选择的特效元数据，如果不应用特效则返回None
        """
        # 获取可用特效（使用VIP资源，100%概率确保每个片段都有特效）
        available_effects = self.metadata_manager.get_available_effects()
        
        if not available_effects:
            return None
        
        # 应用多样性策略
        diverse_effects = self._ensure_effect_diversity(available_effects)
        
        if not diverse_effects:
            # 如果所有特效都用过了，重置历史
            self.used_effects.clear()
            diverse_effects = available_effects
        
        # 基于权重选择特效
        selected_effect = self._weighted_random_choice(
            diverse_effects, 
            self.effect_weights
        )
        
        if selected_effect:
            effect_name = getattr(selected_effect, 'name', '')
            self.used_effects.add(effect_name)
        
        return selected_effect
    
    def generate_random_parameters(self, effect_meta: Any) -> List[Optional[float]]:
        """
        生成随机参数值（轻微效果）

        Args:
            effect_meta: 效果元数据

        Returns:
            List[Optional[float]]: 参数值列表（0-100范围）
        """
        params = getattr(effect_meta, 'params', [])
        if not params:
            return []

        random_params = []

        for param in params:
            # 生成轻微的随机效果参数
            # 根据参数类型智能调整范围，避免过于强烈的效果
            param_name = getattr(param, 'name', '').lower()

            if any(keyword in param_name for keyword in ['亮度', 'brightness', '明度']):
                # 亮度参数：轻微调整，范围15-35（避免过亮或过暗）
                value = random.uniform(15, 35)
            elif any(keyword in param_name for keyword in ['对比度', 'contrast', '对比']):
                # 对比度参数：轻微调整，范围20-40
                value = random.uniform(20, 40)
            elif any(keyword in param_name for keyword in ['饱和度', 'saturation', '饱和']):
                # 饱和度参数：轻微调整，范围25-45
                value = random.uniform(25, 45)
            elif any(keyword in param_name for keyword in ['大小', 'size', '尺寸', '缩放', 'scale']):
                # 大小/缩放参数：轻微调整，范围10-30
                value = random.uniform(10, 30)
            elif any(keyword in param_name for keyword in ['速度', 'speed', '快慢']):
                # 速度参数：轻微调整，范围25-45
                value = random.uniform(25, 45)
            elif any(keyword in param_name for keyword in ['强度', 'intensity', '程度']):
                # 强度参数：轻微效果，范围10-25
                value = random.uniform(10, 25)
            elif any(keyword in param_name for keyword in ['透明度', 'opacity', 'alpha']):
                # 透明度参数：轻微调整，范围20-40
                value = random.uniform(20, 40)
            elif any(keyword in param_name for keyword in ['模糊', 'blur', '虚化']):
                # 模糊参数：轻微模糊，范围5-20
                value = random.uniform(5, 20)
            elif any(keyword in param_name for keyword in ['旋转', 'rotation', 'rotate']):
                # 旋转参数：轻微旋转，范围10-30
                value = random.uniform(10, 30)
            elif any(keyword in param_name for keyword in ['纹理', 'texture', '质感']):
                # 纹理参数：轻微纹理效果，范围15-35
                value = random.uniform(15, 35)
            elif any(keyword in param_name for keyword in ['滤镜', 'filter', '滤波']):
                # 滤镜参数：轻微滤镜效果，范围20-40
                value = random.uniform(20, 40)
            else:
                # 其他参数：使用轻微的正态分布，中心在25，标准差为8
                value = random.normalvariate(25, 8)

            # 确保值在0-100范围内
            value = max(0, min(100, value))
            random_params.append(value)

        return random_params
    
    def _ensure_filter_diversity(self, available_filters: List[Any]) -> List[Any]:
        """确保滤镜多样性"""
        return [f for f in available_filters 
                if getattr(f, 'name', '') not in self.used_filters]
    
    def _ensure_transition_diversity(self, available_transitions: List[Any]) -> List[Any]:
        """确保转场多样性"""
        return [t for t in available_transitions 
                if getattr(t, 'name', '') not in self.used_transitions]
    
    def _ensure_effect_diversity(self, available_effects: List[Any]) -> List[Any]:
        """确保特效多样性"""
        return [e for e in available_effects 
                if getattr(e, 'name', '') not in self.used_effects]
    
    def _weighted_random_choice(self, items: List[Any], weights: Dict[str, float]) -> Optional[Any]:
        """
        基于权重的随机选择
        
        Args:
            items: 候选项列表
            weights: 权重字典
            
        Returns:
            Optional[Any]: 选择的项目
        """
        if not items:
            return None
        
        # 计算权重
        item_weights = []
        for item in items:
            name = getattr(item, 'name', '')
            weight = weights.get(name, 1.0)
            item_weights.append(weight)
        
        # 如果所有权重都为0，使用均匀分布
        if sum(item_weights) == 0:
            return random.choice(items)
        
        # 基于权重随机选择
        return random.choices(items, weights=item_weights)[0]

    def _filter_transitions(self, transitions):
        """过滤转场，排除弹幕类和不适合的转场特效"""
        # 定义要排除的转场关键词
        excluded_keywords = [
            '弹幕', 'danmu', '弹', '幕',
            '评论', '留言', '文字飞入', '字幕',
            '社交', '互动', '点赞', '关注'
        ]

        filtered_transitions = []
        for transition in transitions:
            transition_name = transition.name.lower()

            # 检查是否包含排除的关键词
            should_exclude = False
            for keyword in excluded_keywords:
                if keyword in transition_name:
                    should_exclude = True
                    break

            if not should_exclude:
                filtered_transitions.append(transition)

        print(f"  📊 转场过滤: 从{len(transitions)}个转场过滤到{len(filtered_transitions)}个（排除弹幕类）")
        return filtered_transitions
    
    def _calculate_transition_duration(self, transition_meta: Any, 
                                     prev_segment: Dict[str, Any], 
                                     next_segment: Dict[str, Any]) -> int:
        """
        计算转场时长
        
        Args:
            transition_meta: 转场元数据
            prev_segment: 前一个片段
            next_segment: 下一个片段
            
        Returns:
            int: 转场时长（微秒）
        """
        # 获取默认转场时长
        default_duration = getattr(transition_meta, 'default_duration', 1000000)  # 默认1秒
        
        # 添加一些随机变化（±20%）
        variation = random.uniform(0.8, 1.2)
        duration = int(default_duration * variation)
        
        # 确保转场时长在合理范围内（0.2秒到3秒）
        min_duration = 200000  # 0.2秒
        max_duration = 3000000  # 3秒
        
        duration = max(min_duration, min(max_duration, duration))
        
        return duration
    
    def adjust_effect_weights(self, effect_name: str, weight_multiplier: float, effect_type: str = 'filter'):
        """
        调整效果权重
        
        Args:
            effect_name: 效果名称
            weight_multiplier: 权重乘数
            effect_type: 效果类型 ('filter', 'transition', 'effect')
        """
        if effect_type == 'filter':
            if effect_name in self.filter_weights:
                self.filter_weights[effect_name] *= weight_multiplier
        elif effect_type == 'transition':
            if effect_name in self.transition_weights:
                self.transition_weights[effect_name] *= weight_multiplier
        elif effect_type == 'effect':
            if effect_name in self.effect_weights:
                self.effect_weights[effect_name] *= weight_multiplier
    
    def reset_usage_history(self):
        """重置使用历史"""
        self.used_filters.clear()
        self.used_transitions.clear()
        self.used_effects.clear()
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            'used_filters': len(self.used_filters),
            'used_transitions': len(self.used_transitions),
            'used_effects': len(self.used_effects),
            'filter_names': list(self.used_filters),
            'transition_names': list(self.used_transitions),
            'effect_names': list(self.used_effects)
        }
    
    def print_usage_summary(self):
        """打印使用摘要"""
        stats = self.get_usage_statistics()
        
        print("=== 随机效果引擎使用摘要 ===")
        print(f"已使用滤镜: {stats['used_filters']}个")
        print(f"已使用转场: {stats['used_transitions']}个")
        print(f"已使用特效: {stats['used_effects']}个")
        
        if stats['filter_names']:
            print(f"滤镜列表: {', '.join(stats['filter_names'][:5])}{'...' if len(stats['filter_names']) > 5 else ''}")
        
        if stats['transition_names']:
            print(f"转场列表: {', '.join(stats['transition_names'][:5])}{'...' if len(stats['transition_names']) > 5 else ''}")
        
        if stats['effect_names']:
            print(f"特效列表: {', '.join(stats['effect_names'][:5])}{'...' if len(stats['effect_names']) > 5 else ''}")
        
        print("=============================")
