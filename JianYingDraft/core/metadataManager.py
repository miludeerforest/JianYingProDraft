"""
 * @file   : metadataManager.py
 * @time   : 18:20
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import random
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

# 导入pyJianYingDraft的元数据模块
try:
    from pyJianYingDraft.metadata.filter_meta import Filter_type
    from pyJianYingDraft.metadata.transition_meta import Transition_type, Transition_meta
    from pyJianYingDraft.metadata.video_effect_meta import Video_scene_effect_type
    from pyJianYingDraft.metadata.effect_meta import Effect_meta, Effect_param
except ImportError as e:
    print(f"警告：无法导入pyJianYingDraft元数据模块: {e}")
    # 提供备用的空类定义
    class Filter_type:
        pass
    class Transition_type:
        pass
    class Video_scene_effect_type:
        pass
    class Effect_meta:
        def __init__(self, name, is_vip, resource_id, effect_id, md5, params=None):
            self.name = name
            self.is_vip = is_vip
            self.resource_id = resource_id
            self.effect_id = effect_id
            self.md5 = md5
            self.params = params or []
    class Transition_meta:
        def __init__(self, name, is_vip, resource_id, effect_id, md5, default_duration, is_overlap):
            self.name = name
            self.is_vip = is_vip
            self.resource_id = resource_id
            self.effect_id = effect_id
            self.md5 = md5
            self.default_duration = default_duration
            self.is_overlap = is_overlap


class MetadataManager:
    """
    元数据管理器
    整合pyJianYingDraft的滤镜、转场、特效元数据，提供统一的访问接口
    """
    
    def __init__(self):
        """初始化元数据管理器"""
        self._filters_cache = None
        self._transitions_cache = None
        self._effects_cache = None
        self._load_metadata()
    
    def _load_metadata(self):
        """加载所有元数据"""
        try:
            # 加载滤镜元数据
            self._filters_cache = self._extract_enum_members(Filter_type)
            print(f"加载滤镜元数据: {len(self._filters_cache)} 个")
            
            # 加载转场元数据
            self._transitions_cache = self._extract_enum_members(Transition_type)
            print(f"加载转场元数据: {len(self._transitions_cache)} 个")
            
            # 加载视频特效元数据
            self._effects_cache = self._extract_enum_members(Video_scene_effect_type)
            print(f"加载视频特效元数据: {len(self._effects_cache)} 个")
            
        except Exception as e:
            print(f"加载元数据时出错: {e}")
            # 使用空缓存作为备用
            self._filters_cache = []
            self._transitions_cache = []
            self._effects_cache = []
    
    def _extract_enum_members(self, enum_class) -> List[Any]:
        """从枚举类中提取所有成员"""
        members = []
        try:
            for member in enum_class:
                if hasattr(member, 'value'):
                    members.append(member.value)
        except Exception as e:
            print(f"提取枚举成员时出错 {enum_class}: {e}")
        return members
    
    def get_available_filters(self, vip_only: bool = False, free_only: bool = False) -> List[Effect_meta]:
        """
        获取可用滤镜列表
        
        Args:
            vip_only: 仅返回VIP滤镜
            free_only: 仅返回免费滤镜
            
        Returns:
            List[Effect_meta]: 滤镜元数据列表
        """
        if self._filters_cache is None:
            return []
        
        filters = self._filters_cache.copy()
        
        if vip_only:
            filters = [f for f in filters if getattr(f, 'is_vip', False)]
        elif free_only:
            filters = [f for f in filters if not getattr(f, 'is_vip', False)]
        
        return filters
    
    def get_available_transitions(self, vip_only: bool = False, free_only: bool = False) -> List[Transition_meta]:
        """
        获取可用转场列表
        
        Args:
            vip_only: 仅返回VIP转场
            free_only: 仅返回免费转场
            
        Returns:
            List[Transition_meta]: 转场元数据列表
        """
        if self._transitions_cache is None:
            return []
        
        transitions = self._transitions_cache.copy()
        
        if vip_only:
            transitions = [t for t in transitions if getattr(t, 'is_vip', False)]
        elif free_only:
            transitions = [t for t in transitions if not getattr(t, 'is_vip', False)]
        
        return transitions
    
    def get_available_effects(self, vip_only: bool = False, free_only: bool = False) -> List[Effect_meta]:
        """
        获取可用视频特效列表
        
        Args:
            vip_only: 仅返回VIP特效
            free_only: 仅返回免费特效
            
        Returns:
            List[Effect_meta]: 特效元数据列表
        """
        if self._effects_cache is None:
            return []
        
        effects = self._effects_cache.copy()
        
        if vip_only:
            effects = [e for e in effects if getattr(e, 'is_vip', False)]
        elif free_only:
            effects = [e for e in effects if not getattr(e, 'is_vip', False)]
        
        return effects
    
    def get_random_filter(self, vip_only: bool = False, free_only: bool = False) -> Optional[Effect_meta]:
        """
        随机选择一个滤镜
        
        Args:
            vip_only: 仅从VIP滤镜中选择
            free_only: 仅从免费滤镜中选择
            
        Returns:
            Optional[Effect_meta]: 随机选择的滤镜，如果没有可用滤镜则返回None
        """
        filters = self.get_available_filters(vip_only=vip_only, free_only=free_only)
        if not filters:
            return None
        return random.choice(filters)
    
    def get_random_transition(self, vip_only: bool = False, free_only: bool = False) -> Optional[Transition_meta]:
        """
        随机选择一个转场
        
        Args:
            vip_only: 仅从VIP转场中选择
            free_only: 仅从免费转场中选择
            
        Returns:
            Optional[Transition_meta]: 随机选择的转场，如果没有可用转场则返回None
        """
        transitions = self.get_available_transitions(vip_only=vip_only, free_only=free_only)
        if not transitions:
            return None
        return random.choice(transitions)
    
    def get_random_effect(self, vip_only: bool = False, free_only: bool = False) -> Optional[Effect_meta]:
        """
        随机选择一个视频特效
        
        Args:
            vip_only: 仅从VIP特效中选择
            free_only: 仅从免费特效中选择
            
        Returns:
            Optional[Effect_meta]: 随机选择的特效，如果没有可用特效则返回None
        """
        effects = self.get_available_effects(vip_only=vip_only, free_only=free_only)
        if not effects:
            return None
        return random.choice(effects)
    
    def get_filter_by_name(self, name: str) -> Optional[Effect_meta]:
        """根据名称查找滤镜"""
        filters = self.get_available_filters()
        for filter_meta in filters:
            if getattr(filter_meta, 'name', '') == name:
                return filter_meta
        return None
    
    def get_transition_by_name(self, name: str) -> Optional[Transition_meta]:
        """根据名称查找转场"""
        transitions = self.get_available_transitions()
        for transition_meta in transitions:
            if getattr(transition_meta, 'name', '') == name:
                return transition_meta
        return None
    
    def get_effect_by_name(self, name: str) -> Optional[Effect_meta]:
        """根据名称查找特效"""
        effects = self.get_available_effects()
        for effect_meta in effects:
            if getattr(effect_meta, 'name', '') == name:
                return effect_meta
        return None
    
    def get_metadata_stats(self) -> Dict[str, Any]:
        """获取元数据统计信息"""
        filters = self.get_available_filters()
        transitions = self.get_available_transitions()
        effects = self.get_available_effects()
        
        return {
            'filters': {
                'total': len(filters),
                'free': len([f for f in filters if not getattr(f, 'is_vip', False)]),
                'vip': len([f for f in filters if getattr(f, 'is_vip', False)])
            },
            'transitions': {
                'total': len(transitions),
                'free': len([t for t in transitions if not getattr(t, 'is_vip', False)]),
                'vip': len([t for t in transitions if getattr(t, 'is_vip', False)])
            },
            'effects': {
                'total': len(effects),
                'free': len([e for e in effects if not getattr(e, 'is_vip', False)]),
                'vip': len([e for e in effects if getattr(e, 'is_vip', False)])
            }
        }
    
    def print_metadata_summary(self):
        """打印元数据摘要"""
        stats = self.get_metadata_stats()
        
        print("=== 元数据统计摘要 ===")
        print(f"滤镜: 总计{stats['filters']['total']}个 (免费{stats['filters']['free']}个, VIP{stats['filters']['vip']}个)")
        print(f"转场: 总计{stats['transitions']['total']}个 (免费{stats['transitions']['free']}个, VIP{stats['transitions']['vip']}个)")
        print(f"特效: 总计{stats['effects']['total']}个 (免费{stats['effects']['free']}个, VIP{stats['effects']['vip']}个)")
        print("=====================")
    
    def get_random_selection(self, filter_count: int = 1, transition_count: int = 1, 
                           effect_count: int = 1, use_vip: bool = False) -> Dict[str, List]:
        """
        获取随机选择的元数据组合
        
        Args:
            filter_count: 需要的滤镜数量
            transition_count: 需要的转场数量
            effect_count: 需要的特效数量
            use_vip: 是否使用VIP元数据
            
        Returns:
            Dict[str, List]: 包含随机选择的滤镜、转场、特效的字典
        """
        result = {
            'filters': [],
            'transitions': [],
            'effects': []
        }
        
        # 随机选择滤镜
        for _ in range(filter_count):
            filter_meta = self.get_random_filter(vip_only=use_vip, free_only=not use_vip)
            if filter_meta:
                result['filters'].append(filter_meta)
        
        # 随机选择转场
        for _ in range(transition_count):
            transition_meta = self.get_random_transition(vip_only=use_vip, free_only=not use_vip)
            if transition_meta:
                result['transitions'].append(transition_meta)
        
        # 随机选择特效
        for _ in range(effect_count):
            effect_meta = self.get_random_effect(vip_only=use_vip, free_only=not use_vip)
            if effect_meta:
                result['effects'].append(effect_meta)
        
        return result
