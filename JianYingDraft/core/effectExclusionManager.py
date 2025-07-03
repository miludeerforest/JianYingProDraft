"""
特效排除管理器 - 管理用户自定义的特效、滤镜、转场排除列表
"""
import json
import os
from typing import Set, List, Dict, Any
from .metadataManager import MetadataManager


class EffectExclusionManager:
    """特效排除管理器"""
    
    def __init__(self, config_file: str = "excluded_effects.json"):
        """
        初始化特效排除管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.metadata_manager = MetadataManager()
        self.excluded_filters: Set[str] = set()
        self.excluded_effects: Set[str] = set()
        self.excluded_transitions: Set[str] = set()
        self.load_exclusions()
    
    def load_exclusions(self):
        """加载排除列表"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.excluded_filters = set(data.get('filters', []))
                    self.excluded_effects = set(data.get('effects', []))
                    self.excluded_transitions = set(data.get('transitions', []))
        except Exception as e:
            print(f"⚠️  加载排除列表失败: {e}")
            self.excluded_filters = set()
            self.excluded_effects = set()
            self.excluded_transitions = set()
    
    def save_exclusions(self):
        """保存排除列表"""
        try:
            data = {
                'filters': list(self.excluded_filters),
                'effects': list(self.excluded_effects),
                'transitions': list(self.excluded_transitions)
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存排除列表失败: {e}")
    
    def add_excluded_filter(self, filter_name: str) -> bool:
        """添加排除滤镜"""
        if filter_name not in self.excluded_filters:
            self.excluded_filters.add(filter_name)
            self.save_exclusions()
            return True
        return False
    
    def remove_excluded_filter(self, filter_name: str) -> bool:
        """移除排除滤镜"""
        if filter_name in self.excluded_filters:
            self.excluded_filters.remove(filter_name)
            self.save_exclusions()
            return True
        return False
    
    def add_excluded_effect(self, effect_name: str) -> bool:
        """添加排除特效"""
        if effect_name not in self.excluded_effects:
            self.excluded_effects.add(effect_name)
            self.save_exclusions()
            return True
        return False
    
    def remove_excluded_effect(self, effect_name: str) -> bool:
        """移除排除特效"""
        if effect_name in self.excluded_effects:
            self.excluded_effects.remove(effect_name)
            self.save_exclusions()
            return True
        return False
    
    def add_excluded_transition(self, transition_name: str) -> bool:
        """添加排除转场"""
        if transition_name not in self.excluded_transitions:
            self.excluded_transitions.add(transition_name)
            self.save_exclusions()
            return True
        return False
    
    def remove_excluded_transition(self, transition_name: str) -> bool:
        """移除排除转场"""
        if transition_name in self.excluded_transitions:
            self.excluded_transitions.remove(transition_name)
            self.save_exclusions()
            return True
        return False
    
    def get_filtered_filters(self) -> List[Any]:
        """获取过滤后的滤镜列表"""
        all_filters = self.metadata_manager.get_available_filters()
        return [f for f in all_filters if f.name not in self.excluded_filters]
    
    def get_filtered_effects(self) -> List[Any]:
        """获取过滤后的特效列表"""
        all_effects = self.metadata_manager.get_available_effects()
        return [e for e in all_effects if e.name not in self.excluded_effects]
    
    def get_filtered_transitions(self) -> List[Any]:
        """获取过滤后的转场列表"""
        all_transitions = self.metadata_manager.get_available_transitions()
        # 先应用弹幕过滤
        filtered_transitions = self._filter_danmu_transitions(all_transitions)
        # 再应用用户排除
        return [t for t in filtered_transitions if t.name not in self.excluded_transitions]
    
    def _filter_danmu_transitions(self, transitions):
        """过滤弹幕类转场（保持与原有逻辑一致）"""
        excluded_keywords = [
            '弹幕', 'danmu', '弹', '幕',
            '评论', '留言', '文字飞入', '字幕',
            '社交', '互动', '点赞', '关注'
        ]
        
        filtered_transitions = []
        for transition in transitions:
            transition_name = transition.name.lower()
            
            should_exclude = False
            for keyword in excluded_keywords:
                if keyword in transition_name:
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_transitions.append(transition)
        
        return filtered_transitions
    
    def clear_all_exclusions(self):
        """清空所有排除列表"""
        self.excluded_filters.clear()
        self.excluded_effects.clear()
        self.excluded_transitions.clear()
        self.save_exclusions()
    
    def get_exclusion_stats(self) -> Dict[str, int]:
        """获取排除统计信息"""
        return {
            'filters': len(self.excluded_filters),
            'effects': len(self.excluded_effects),
            'transitions': len(self.excluded_transitions)
        }
    
    def export_exclusions(self, file_path: str) -> bool:
        """导出排除列表"""
        try:
            data = {
                'filters': list(self.excluded_filters),
                'effects': list(self.excluded_effects),
                'transitions': list(self.excluded_transitions),
                'export_info': {
                    'version': '1.0',
                    'description': '特效排除列表导出文件'
                }
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  导出失败: {e}")
            return False
    
    def import_exclusions(self, file_path: str) -> bool:
        """导入排除列表"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 合并导入的排除列表
            imported_filters = set(data.get('filters', []))
            imported_effects = set(data.get('effects', []))
            imported_transitions = set(data.get('transitions', []))
            
            self.excluded_filters.update(imported_filters)
            self.excluded_effects.update(imported_effects)
            self.excluded_transitions.update(imported_transitions)
            
            self.save_exclusions()
            return True
        except Exception as e:
            print(f"⚠️  导入失败: {e}")
            return False
    
    def find_effects_by_keyword(self, keyword: str, effect_type: str = 'all') -> List[str]:
        """根据关键词查找特效"""
        results = []
        
        if effect_type in ['all', 'filters']:
            all_filters = self.metadata_manager.get_available_filters()
            for f in all_filters:
                if keyword.lower() in f.name.lower():
                    results.append(f"滤镜: {f.name}")
        
        if effect_type in ['all', 'effects']:
            all_effects = self.metadata_manager.get_available_effects()
            for e in all_effects:
                if keyword.lower() in e.name.lower():
                    results.append(f"特效: {e.name}")
        
        if effect_type in ['all', 'transitions']:
            all_transitions = self.metadata_manager.get_available_transitions()
            for t in all_transitions:
                if keyword.lower() in t.name.lower():
                    results.append(f"转场: {t.name}")
        
        return results
