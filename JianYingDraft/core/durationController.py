"""
 * @file   : durationController.py
 * @time   : 20:45
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import random
import math
from typing import List, Dict, Any, Optional, Tuple
from JianYingDraft.core.configManager import AutoMixConfigManager


class DurationController:
    """
    时长控制器
    实现30-40秒总时长的精确控制和智能分配算法
    """
    
    def __init__(self, config_manager: AutoMixConfigManager = None):
        """
        初始化时长控制器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager or AutoMixConfigManager
        
        # 获取配置参数
        self.min_total_duration, self.max_total_duration = self.config_manager.get_video_duration_range()
        self.min_segment_duration = 2000000  # 最小片段时长2秒
        self.max_segment_duration = 15000000  # 最大片段时长15秒
        self.default_transition_duration = 1000000  # 默认转场时长1秒
        
        # 时长分配策略参数
        self.priority_weight_factor = 1.5  # 优先级权重因子
        self.duration_variance = 0.2  # 时长变化范围（±20%）
    
    def calculate_segment_durations(self, materials: List[Dict[str, Any]], 
                                  target_duration: Optional[int] = None,
                                  priorities: Optional[List[float]] = None) -> List[int]:
        """
        计算每个片段的时长分配
        
        Args:
            materials: 素材信息列表
            target_duration: 目标总时长（微秒），如果为None则随机选择30-40秒范围内的值
            priorities: 优先级列表，值越大优先级越高
            
        Returns:
            List[int]: 每个片段的时长列表（微秒）
        """
        if not materials:
            return []
        
        # 确定目标总时长
        if target_duration is None:
            target_duration = random.randint(self.min_total_duration, self.max_total_duration)
        
        # 确保目标时长在合理范围内
        target_duration = max(self.min_total_duration, min(self.max_total_duration, target_duration))
        
        # 初始化优先级
        if priorities is None:
            priorities = [1.0] * len(materials)
        elif len(priorities) != len(materials):
            # 如果优先级数量不匹配，使用默认值
            priorities = [1.0] * len(materials)
        
        # 计算基础时长分配
        segment_count = len(materials)
        
        # 预留转场时长（转场数量 = 片段数量 - 1）
        transition_count = max(0, segment_count - 1)
        total_transition_duration = transition_count * self.default_transition_duration
        
        # 可用于片段的总时长
        available_duration = target_duration - total_transition_duration
        
        if available_duration <= 0:
            raise ValueError(f"目标时长({target_duration/1000000:.1f}s)太短，无法容纳{segment_count}个片段和{transition_count}个转场")
        
        # 基于优先级和素材原始时长计算权重
        weights = self._calculate_segment_weights(materials, priorities)
        
        # 分配时长
        durations = self._allocate_durations(available_duration, weights, materials)
        
        # 验证和调整时长
        durations = self._validate_and_adjust_durations(durations, available_duration)
        
        return durations
    
    def _calculate_segment_weights(self, materials: List[Dict[str, Any]], 
                                 priorities: List[float]) -> List[float]:
        """
        计算片段权重
        
        Args:
            materials: 素材信息列表
            priorities: 优先级列表
            
        Returns:
            List[float]: 权重列表
        """
        weights = []
        
        for i, (material, priority) in enumerate(zip(materials, priorities)):
            # 基础权重
            base_weight = 1.0
            
            # 优先级权重
            priority_weight = priority * self.priority_weight_factor
            
            # 素材时长权重（较长的素材可以分配更多时间）
            material_duration = material.get('available_duration', material.get('duration', 0))
            if material_duration > 0:
                # 标准化素材时长权重（相对于5秒基准）
                duration_weight = min(2.0, material_duration / 5000000)
            else:
                duration_weight = 1.0
            
            # 综合权重
            total_weight = base_weight * priority_weight * duration_weight
            weights.append(total_weight)
        
        return weights
    
    def _allocate_durations(self, available_duration: int, weights: List[float],
                          materials: List[Dict[str, Any]]) -> List[int]:
        """
        根据权重分配时长

        Args:
            available_duration: 可用总时长
            weights: 权重列表
            materials: 素材信息列表

        Returns:
            List[int]: 分配的时长列表
        """
        total_weight = sum(weights)
        if total_weight == 0:
            # 如果总权重为0，平均分配
            avg_duration = available_duration // len(weights)
            return [avg_duration] * len(weights)

        durations = []

        # 第一轮：按权重分配基础时长
        for weight, material in zip(weights, materials):
            # 按权重分配
            duration = int(available_duration * weight / total_weight)

            # 限制在素材可用时长内
            material_duration = material.get('available_duration', material.get('duration', 0))
            if material_duration > 0:
                duration = min(duration, material_duration)

            durations.append(duration)

        # 第二轮：添加随机变化并确保总时长正确
        if self.duration_variance > 0:
            for i in range(len(durations)):
                variance = durations[i] * self.duration_variance
                random_change = random.randint(int(-variance), int(variance))
                durations[i] += random_change

        # 第三轮：调整总时长以匹配目标
        current_total = sum(durations)
        if current_total != available_duration:
            difference = available_duration - current_total
            # 将差值平均分配到所有片段
            per_segment_adjustment = difference // len(durations)
            remainder = difference % len(durations)

            for i in range(len(durations)):
                durations[i] += per_segment_adjustment
                if i < remainder:
                    durations[i] += 1

        return durations
    
    def _validate_and_adjust_durations(self, durations: List[int], 
                                     available_duration: int) -> List[int]:
        """
        验证和调整时长分配
        
        Args:
            durations: 原始时长列表
            available_duration: 可用总时长
            
        Returns:
            List[int]: 调整后的时长列表
        """
        adjusted_durations = []
        
        # 第一步：确保每个片段时长在合理范围内
        for duration in durations:
            adjusted_duration = max(self.min_segment_duration, 
                                  min(self.max_segment_duration, duration))
            adjusted_durations.append(adjusted_duration)
        
        # 第二步：调整总时长
        current_total = sum(adjusted_durations)
        
        if current_total != available_duration:
            # 计算差值
            difference = available_duration - current_total
            
            if difference > 0:
                # 需要增加时长，优先给较短的片段增加
                self._distribute_extra_duration(adjusted_durations, difference)
            else:
                # 需要减少时长，优先从较长的片段减少
                self._reduce_excess_duration(adjusted_durations, -difference)
        
        return adjusted_durations
    
    def _distribute_extra_duration(self, durations: List[int], extra_duration: int):
        """分配额外时长"""
        remaining = extra_duration
        
        while remaining > 0 and any(d < self.max_segment_duration for d in durations):
            # 找到最短的片段
            min_duration = min(durations)
            min_indices = [i for i, d in enumerate(durations) if d == min_duration]
            
            # 为最短的片段增加时长
            for i in min_indices:
                if remaining <= 0:
                    break
                if durations[i] < self.max_segment_duration:
                    increment = min(remaining, 100000, self.max_segment_duration - durations[i])  # 每次增加0.1秒
                    durations[i] += increment
                    remaining -= increment
    
    def _reduce_excess_duration(self, durations: List[int], excess_duration: int):
        """减少多余时长"""
        remaining = excess_duration
        
        while remaining > 0 and any(d > self.min_segment_duration for d in durations):
            # 找到最长的片段
            max_duration = max(durations)
            max_indices = [i for i, d in enumerate(durations) if d == max_duration]
            
            # 从最长的片段减少时长
            for i in max_indices:
                if remaining <= 0:
                    break
                if durations[i] > self.min_segment_duration:
                    decrement = min(remaining, 100000, durations[i] - self.min_segment_duration)  # 每次减少0.1秒
                    durations[i] -= decrement
                    remaining -= decrement
    
    def adjust_for_transitions(self, segment_durations: List[int], 
                             transition_durations: List[int]) -> Tuple[List[int], int]:
        """
        考虑转场时长调整片段时长
        
        Args:
            segment_durations: 片段时长列表
            transition_durations: 转场时长列表
            
        Returns:
            Tuple[List[int], int]: (调整后的片段时长列表, 总时长)
        """
        if not segment_durations:
            return [], 0
        
        # 计算当前总时长
        total_segment_duration = sum(segment_durations)
        total_transition_duration = sum(transition_durations)
        current_total = total_segment_duration + total_transition_duration
        
        # 检查是否需要调整
        if self.min_total_duration <= current_total <= self.max_total_duration:
            return segment_durations, current_total
        
        # 计算目标片段总时长
        target_total = random.randint(self.min_total_duration, self.max_total_duration)
        target_segment_duration = target_total - total_transition_duration
        
        if target_segment_duration <= 0:
            raise ValueError("转场时长过长，无法满足总时长要求")
        
        # 按比例调整片段时长
        scale_factor = target_segment_duration / total_segment_duration
        adjusted_durations = [int(duration * scale_factor) for duration in segment_durations]
        
        # 验证调整后的时长
        adjusted_durations = self._validate_and_adjust_durations(
            adjusted_durations, target_segment_duration
        )
        
        final_total = sum(adjusted_durations) + total_transition_duration
        
        return adjusted_durations, final_total
    
    def validate_total_duration(self, segment_durations: List[int], 
                              transition_durations: List[int] = None) -> Tuple[bool, str]:
        """
        验证总时长是否在30-40秒范围内
        
        Args:
            segment_durations: 片段时长列表
            transition_durations: 转场时长列表
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not segment_durations:
            return False, "没有片段时长数据"
        
        total_segment_duration = sum(segment_durations)
        
        if transition_durations:
            total_transition_duration = sum(transition_durations)
        else:
            # 使用默认转场时长估算
            transition_count = max(0, len(segment_durations) - 1)
            total_transition_duration = transition_count * self.default_transition_duration
        
        total_duration = total_segment_duration + total_transition_duration
        
        if total_duration < self.min_total_duration:
            return False, f"总时长({total_duration/1000000:.1f}s)小于最小要求({self.min_total_duration/1000000:.1f}s)"
        
        if total_duration > self.max_total_duration:
            return False, f"总时长({total_duration/1000000:.1f}s)大于最大限制({self.max_total_duration/1000000:.1f}s)"
        
        return True, "时长验证通过"
    
    def optimize_duration_distribution(self, materials: List[Dict[str, Any]], 
                                     target_duration: int) -> Dict[str, Any]:
        """
        优化时长分配算法
        
        Args:
            materials: 素材信息列表
            target_duration: 目标总时长
            
        Returns:
            Dict[str, Any]: 优化结果
        """
        if not materials:
            return {'success': False, 'error': '没有素材数据'}
        
        try:
            # 计算基础分配
            durations = self.calculate_segment_durations(materials, target_duration)
            
            # 计算转场时长
            transition_count = max(0, len(materials) - 1)
            transition_durations = [self.default_transition_duration] * transition_count
            
            # 调整考虑转场
            adjusted_durations, final_total = self.adjust_for_transitions(durations, transition_durations)
            
            # 验证结果
            is_valid, message = self.validate_total_duration(adjusted_durations, transition_durations)
            
            return {
                'success': is_valid,
                'segment_durations': adjusted_durations,
                'transition_durations': transition_durations,
                'total_duration': final_total,
                'target_duration': target_duration,
                'message': message,
                'statistics': {
                    'segment_count': len(adjusted_durations),
                    'transition_count': len(transition_durations),
                    'avg_segment_duration': sum(adjusted_durations) / len(adjusted_durations) if adjusted_durations else 0,
                    'total_segment_duration': sum(adjusted_durations),
                    'total_transition_duration': sum(transition_durations)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def handle_insufficient_material(self, available_duration: int, 
                                   target_duration: int) -> Dict[str, Any]:
        """
        处理素材时长不足的情况
        
        Args:
            available_duration: 可用素材总时长
            target_duration: 目标总时长
            
        Returns:
            Dict[str, Any]: 处理建议
        """
        if available_duration >= target_duration:
            return {'sufficient': True, 'message': '素材时长充足'}
        
        shortage = target_duration - available_duration
        
        suggestions = []
        
        # 建议1：降低目标时长
        min_target = max(self.min_total_duration, available_duration)
        if min_target >= self.min_total_duration:
            suggestions.append({
                'type': 'reduce_target',
                'description': f'降低目标时长到{min_target/1000000:.1f}秒',
                'new_target': min_target
            })
        
        # 建议2：重复使用素材
        if available_duration > 0:
            repeat_factor = math.ceil(target_duration / available_duration)
            suggestions.append({
                'type': 'repeat_materials',
                'description': f'重复使用素材{repeat_factor}次',
                'repeat_factor': repeat_factor
            })
        
        # 建议3：添加更多素材
        suggestions.append({
            'type': 'add_materials',
            'description': f'需要添加{shortage/1000000:.1f}秒的额外素材',
            'needed_duration': shortage
        })
        
        return {
            'sufficient': False,
            'available_duration': available_duration,
            'target_duration': target_duration,
            'shortage': shortage,
            'suggestions': suggestions
        }
