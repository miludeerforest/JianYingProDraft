#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
剪映自动混剪工具 - 重构版Web界面
性能优化版本，支持一级二级菜单结构
"""

import os
import sys
import json
import threading
import time
from flask import Flask, render_template, jsonify, request
import webbrowser

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 检查并导入核心模块
try:
    # 尝试从JianYingDraft.core导入
    from JianYingDraft.core.configManager import ConfigManager
    from JianYingDraft.core.effectExclusionManager import EffectExclusionManager
    from JianYingDraft.core.standardAutoMix import StandardAutoMix
except ImportError:
    try:
        # 尝试从当前目录的core导入
        from core.configManager import ConfigManager
        from core.effectExclusionManager import EffectExclusionManager
        from core.standardAutoMix import StandardAutoMix
    except ImportError as e:
        print(f"❌ 无法导入核心模块: {e}")
        print("请确保JianYingDraft/core目录存在并包含必要的Python文件")
        sys.exit(1)

class OptimizedWebInterface:
    """优化版Web界面类"""
    
    def __init__(self):
        """初始化Web界面"""
        self.config_manager = ConfigManager()
        self.exclusion_manager = EffectExclusionManager()
        self.automix_status = {
            'running': False,
            'progress': '',
            'error': None,
            'result': None
        }

        # 任务统计跟踪
        self.task_statistics = {
            'completed_today': 0,
            'error_count_today': 0,
            'last_reset_date': None
        }

        # 缓存数据，减少重复计算
        self._cache = {
            'config': None,
            'exclusions': None,
            'effects': None,
            'products': None,
            'cache_time': 0
        }
        self._cache_timeout = 30  # 缓存30秒

        # 初始化今日统计
        self._reset_daily_statistics_if_needed()

    def _reset_daily_statistics_if_needed(self):
        """如果是新的一天，重置统计数据"""
        import datetime
        today = datetime.date.today()

        if self.task_statistics['last_reset_date'] != today:
            self.task_statistics['completed_today'] = 0
            self.task_statistics['error_count_today'] = 0
            self.task_statistics['last_reset_date'] = today

    def _increment_completed_tasks(self):
        """增加完成任务计数"""
        self._reset_daily_statistics_if_needed()
        self.task_statistics['completed_today'] += 1

    def _increment_error_count(self):
        """增加错误计数"""
        self._reset_daily_statistics_if_needed()
        self.task_statistics['error_count_today'] += 1

    def _is_cache_valid(self):
        """检查缓存是否有效"""
        return time.time() - self._cache['cache_time'] < self._cache_timeout
    
    def _update_cache_time(self):
        """更新缓存时间"""
        self._cache['cache_time'] = time.time()
    
    def get_config_info(self):
        """获取配置信息（带缓存）"""
        if self._cache['config'] and self._is_cache_valid():
            return self._cache['config']
        
        try:
            config = {}
            
            # 基础路径配置
            config['material_path'] = self.config_manager.get_material_path()
            config['draft_output_path'] = self.config_manager.get_draft_output_path()
            
            # 视频参数
            min_dur, max_dur = self.config_manager.get_video_duration_range()
            config['video_duration_min'] = min_dur // 1000000
            config['video_duration_max'] = max_dur // 1000000
            config['video_scale_factor'] = self.config_manager.get_video_scale_factor()
            
            # 音频设置
            config['narration_volume'] = self.config_manager.get_narration_volume()
            config['background_volume'] = self.config_manager.get_background_volume()
            
            # 滤镜强度
            min_intensity, max_intensity = self.config_manager.get_filter_intensity_range()
            config['filter_intensity_min'] = min_intensity
            config['filter_intensity_max'] = max_intensity
            
            # 批量生成
            config['batch_count'] = self.config_manager.get_batch_count()
            
            # 防审核配置
            config['pexels_overlay_enabled'] = self.config_manager.is_pexels_overlay_enabled()
            config['pexels_overlay_opacity'] = self.config_manager.get_pexels_overlay_opacity()

            # 高级防审核技术配置
            config['flip_probability'] = self.config_manager.get_flip_probability()
            config['blur_background_enabled'] = self.config_manager.is_blur_background_enabled()
            config['blur_background_probability'] = self.config_manager.get_blur_background_probability()
            config['foreground_scale'] = self.config_manager.get_foreground_scale()
            config['background_scale'] = self.config_manager.get_background_scale()
            config['background_blur_intensity'] = self.config_manager.get_background_blur_intensity()
            config['frame_manipulation_enabled'] = self.config_manager.is_frame_manipulation_enabled()
            config['frame_drop_probability'] = self.config_manager.get_frame_drop_probability()
            config['frame_drop_interval'] = self.config_manager.get_frame_drop_interval()
            config['max_frame_drops_per_segment'] = self.config_manager.get_max_frame_drops_per_segment()

            # 版本信息和特效参数说明
            config['version_info'] = {
                'version': '2.1.0',
                'last_updated': '2025-07-05',
                'features': [
                    '轻微特效参数优化',
                    '纹理和滤镜参数支持',
                    '智能编码检测修复',
                    '界面性能重构'
                ]
            }

            config['effect_params_info'] = {
                '亮度': '15-35 (轻微调整)',
                '对比度': '20-40 (轻微调整)',
                '饱和度': '25-45 (轻微调整)',
                '大小': '10-30 (轻微缩放)',
                '速度': '25-45 (轻微变速)',
                '强度': '10-25 (轻微强度)',
                '透明度': '20-40 (轻微透明)',
                '模糊': '5-20 (轻微模糊)',
                '旋转': '10-30 (轻微旋转)',
                '纹理': '15-35 (轻微纹理)',
                '滤镜': '20-40 (轻微滤镜)',
                '其他': '中心25±8 (轻微正态分布)'
            }

            # 缓存结果
            self._cache['config'] = config
            self._update_cache_time()
            
            return config
        except Exception as e:
            return {'error': str(e)}
    
    def get_exclusion_stats(self):
        """获取排除统计信息（带缓存）"""
        if self._cache['exclusions'] and self._is_cache_valid():
            return self._cache['exclusions']
        
        try:
            stats = {}
            
            # 获取各类型统计
            video_effects = self.exclusion_manager.excluded_effects
            filters = self.exclusion_manager.excluded_filters
            transitions = self.exclusion_manager.excluded_transitions
            
            stats['video_effects'] = {
                'total': 912,
                'excluded': len(video_effects),
                'available': 912 - len(video_effects)
            }
            
            stats['filters'] = {
                'total': 468,
                'excluded': len(filters),
                'available': 468 - len(filters)
            }
            
            stats['transitions'] = {
                'total': 362,
                'excluded': len(transitions),
                'available': 362 - len(transitions)
            }
            
            # 缓存结果
            self._cache['exclusions'] = stats
            self._update_cache_time()
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def update_config(self, config_data):
        """更新配置"""
        try:
            success = True
            errors = []
            
            # 更新各项配置
            for key, value in config_data.items():
                try:
                    if key == 'material_path':
                        success &= self.config_manager._set_config_value('material_path', value)
                    elif key == 'draft_output_path':
                        success &= self.config_manager._set_config_value('draft_output_path', value)
                    elif key == 'video_duration_min':
                        success &= self.config_manager._set_config_value('video_duration_min', int(value) * 1000000)
                    elif key == 'video_duration_max':
                        success &= self.config_manager._set_config_value('video_duration_max', int(value) * 1000000)
                    elif key == 'video_scale_factor':
                        success &= self.config_manager._set_config_value('video_scale_factor', float(value))
                    elif key == 'narration_volume':
                        success &= self.config_manager._set_config_value('narration_volume', float(value))
                    elif key == 'background_volume':
                        success &= self.config_manager._set_config_value('background_volume', float(value))
                    elif key == 'filter_intensity_min':
                        success &= self.config_manager._set_config_value('filter_intensity_min', int(value))
                    elif key == 'filter_intensity_max':
                        success &= self.config_manager._set_config_value('filter_intensity_max', int(value))
                    elif key == 'batch_count':
                        success &= self.config_manager._set_config_value('batch_count', int(value))
                    # 高级防审核技术配置
                    elif key == 'flip_probability':
                        success &= self.config_manager.set_flip_probability(float(value))
                    elif key == 'blur_background_enabled':
                        success &= self.config_manager.set_blur_background_enabled(bool(value))
                    elif key == 'blur_background_probability':
                        success &= self.config_manager.set_blur_background_probability(float(value))
                    elif key == 'foreground_scale':
                        success &= self.config_manager.set_foreground_scale(float(value))
                    elif key == 'background_scale':
                        success &= self.config_manager.set_background_scale(float(value))
                    elif key == 'background_blur_intensity':
                        success &= self.config_manager.set_background_blur_intensity(float(value))
                    elif key == 'frame_manipulation_enabled':
                        success &= self.config_manager.set_frame_manipulation_enabled(bool(value))
                    elif key == 'frame_drop_probability':
                        success &= self.config_manager.set_frame_drop_probability(float(value))
                    elif key == 'frame_drop_interval':
                        success &= self.config_manager.set_frame_drop_interval(float(value))
                    elif key == 'max_frame_drops_per_segment':
                        success &= self.config_manager.set_max_frame_drops_per_segment(int(value))
                except Exception as e:
                    errors.append(f"{key}: {str(e)}")
            
            # 清除配置缓存
            self._cache['config'] = None
            
            return {'success': success, 'errors': errors}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def get_available_products(self):
        """获取可用产品列表（带缓存）"""
        if self._cache['products'] and self._is_cache_valid():
            return self._cache['products']
        
        try:
            material_path = self.config_manager.get_material_path()
            if not os.path.exists(material_path):
                return {'success': False, 'error': '素材库路径不存在'}

            products = []
            for item in os.listdir(material_path):
                item_path = os.path.join(material_path, item)
                if os.path.isdir(item_path):
                    # 检查是否包含视频文件
                    has_videos = False
                    for root, dirs, files in os.walk(item_path):
                        for file in files:
                            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                                has_videos = True
                                break
                        if has_videos:
                            break
                    
                    if has_videos:
                        products.append({
                            'name': item,
                            'path': item_path
                        })
            
            result = {'success': True, 'products': products}
            
            # 缓存结果
            self._cache['products'] = result
            self._update_cache_time()
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def start_single_automix(self, product, duration):
        """启动单个混剪任务"""
        try:
            if self.automix_status['running']:
                return {'success': False, 'error': '已有混剪任务在运行中'}

            # 更新状态
            self.automix_status['running'] = True
            self.automix_status['progress'] = '正在初始化混剪任务...'
            self.automix_status['error'] = None
            self.automix_status['result'] = None

            # 在后台线程中执行混剪
            def run_automix():
                try:
                    # 调用真正的混剪逻辑
                    from JianYingDraft.core.standardAutoMix import StandardAutoMix

                    # 创建草稿名称
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    draft_name = f"{product}_单个混剪_{duration}s_{timestamp}"

                    self.automix_status['progress'] = f'正在为产品 {product} 生成 {duration}秒 混剪视频...'

                    # 创建StandardAutoMix实例
                    automix = StandardAutoMix(draft_name)

                    # 设置进度回调
                    def progress_callback(message, progress):
                        self.automix_status['progress'] = f'{message} ({progress:.1f}%)'

                    automix.progress_callback = progress_callback

                    # 执行混剪 (duration秒转换为微秒)
                    target_duration = duration * 1000000  # 秒转微秒
                    result = automix.auto_mix(target_duration=target_duration, product_model=product)

                    if result.get('success', False):
                        # 混剪成功，提取统计信息
                        statistics = result.get('statistics', {})
                        self.automix_status['running'] = False
                        self.automix_status['progress'] = '混剪完成'
                        self.automix_status['result'] = {
                            'draft_name': draft_name,
                            'draft_path': result.get('draft_path', ''),
                            'duration': duration,
                            'video_count': statistics.get('selected_materials', 0),
                            'effects_count': statistics.get('applied_effects', 0),
                            'transitions_count': statistics.get('applied_transitions', 0),
                            'filters_count': statistics.get('applied_filters', 0)
                        }

                        # 更新完成任务统计
                        self._increment_completed_tasks()
                    else:
                        # 混剪失败
                        self.automix_status['running'] = False
                        self.automix_status['error'] = result.get('error', '未知错误')
                        self.automix_status['progress'] = '混剪失败'

                        # 更新错误统计
                        self._increment_error_count()

                except Exception as e:
                    self.automix_status['running'] = False
                    self.automix_status['error'] = str(e)
                    self.automix_status['progress'] = '混剪失败'

                    # 更新错误统计
                    self._increment_error_count()

            # 启动后台线程
            threading.Thread(target=run_automix, daemon=True).start()

            return {'success': True, 'message': '混剪任务已启动'}

        except Exception as e:
            self.automix_status['running'] = False
            return {'success': False, 'error': str(e)}

    def start_batch_automix(self, product, count, min_duration, max_duration):
        """启动批量混剪任务"""
        try:
            if self.automix_status['running']:
                return {'success': False, 'error': '已有混剪任务在运行中'}

            # 更新状态
            self.automix_status['running'] = True
            self.automix_status['progress'] = f'正在初始化批量混剪任务 (共{count}个)...'
            self.automix_status['error'] = None
            self.automix_status['result'] = None

            # 在后台线程中执行批量混剪
            def run_batch_automix():
                try:
                    from JianYingDraft.core.standardAutoMix import StandardAutoMix
                    import datetime
                    import random

                    results = []
                    successful_count = 0
                    failed_count = 0

                    for i in range(count):
                        current_duration = random.randint(min_duration, max_duration)
                        self.automix_status['progress'] = f'正在生成第 {i+1}/{count} 个视频 ({current_duration}秒)...'

                        try:
                            # 创建草稿名称
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            draft_name = f"{product}_批量_{i+1:02d}_{current_duration}s_{timestamp}"

                            # 创建StandardAutoMix实例
                            automix = StandardAutoMix(draft_name)

                            # 设置进度回调
                            def progress_callback(message, progress):
                                self.automix_status['progress'] = f'第{i+1}/{count}个: {message} ({progress:.1f}%)'

                            automix.progress_callback = progress_callback

                            # 执行混剪
                            target_duration = current_duration * 1000000  # 秒转微秒
                            mix_result = automix.auto_mix(target_duration=target_duration, product_model=product)

                            if mix_result.get('success', False):
                                # 提取统计信息
                                statistics = mix_result.get('statistics', {})
                                result = {
                                    'index': i + 1,
                                    'draft_name': draft_name,
                                    'draft_path': mix_result.get('draft_path', ''),
                                    'duration': current_duration,
                                    'video_count': statistics.get('selected_materials', 0),
                                    'effects_count': statistics.get('applied_effects', 0),
                                    'transitions_count': statistics.get('applied_transitions', 0),
                                    'filters_count': statistics.get('applied_filters', 0),
                                    'status': 'success'
                                }
                                successful_count += 1
                            else:
                                result = {
                                    'index': i + 1,
                                    'draft_name': draft_name,
                                    'duration': current_duration,
                                    'error': mix_result.get('error', '未知错误'),
                                    'status': 'failed'
                                }
                                failed_count += 1

                            results.append(result)

                        except Exception as e:
                            result = {
                                'index': i + 1,
                                'duration': current_duration,
                                'error': str(e),
                                'status': 'failed'
                            }
                            results.append(result)
                            failed_count += 1

                    # 批量混剪完成
                    self.automix_status['running'] = False
                    self.automix_status['progress'] = f'批量混剪完成: 成功{successful_count}个, 失败{failed_count}个'
                    self.automix_status['result'] = {
                        'total_count': count,
                        'successful_count': successful_count,
                        'failed_count': failed_count,
                        'results': results,
                        'total_duration': sum(r['duration'] for r in results)
                    }

                    # 更新统计数据
                    for _ in range(successful_count):
                        self._increment_completed_tasks()
                    for _ in range(failed_count):
                        self._increment_error_count()

                except Exception as e:
                    self.automix_status['running'] = False
                    self.automix_status['error'] = str(e)
                    self.automix_status['progress'] = '批量混剪失败'

                    # 更新错误统计
                    self._increment_error_count()

            # 启动后台线程
            threading.Thread(target=run_batch_automix, daemon=True).start()

            return {'success': True, 'message': f'批量混剪任务已启动 (共{count}个视频)'}

        except Exception as e:
            self.automix_status['running'] = False
            return {'success': False, 'error': str(e)}

    def search_effects(self, search_term, effect_type):
        """搜索特效"""
        try:
            effects = []

            # 模拟特效数据 - 实际应该从元数据文件加载
            if effect_type == 'all' or effect_type == 'video_effects':
                # 模拟视频特效
                for i in range(1, 21):  # 显示20个示例
                    effect_name = f"视频特效_{i:03d}"
                    if not search_term or search_term.lower() in effect_name.lower():
                        effects.append({
                            'id': f'video_effect_{i}',
                            'name': effect_name,
                            'type': '视频特效',
                            'excluded': effect_name in self.exclusion_manager.excluded_effects
                        })

            if effect_type == 'all' or effect_type == 'filters':
                # 模拟滤镜
                for i in range(1, 21):
                    filter_name = f"滤镜_{i:03d}"
                    if not search_term or search_term.lower() in filter_name.lower():
                        effects.append({
                            'id': f'filter_{i}',
                            'name': filter_name,
                            'type': '滤镜',
                            'excluded': filter_name in self.exclusion_manager.excluded_filters
                        })

            if effect_type == 'all' or effect_type == 'transitions':
                # 模拟转场
                for i in range(1, 21):
                    transition_name = f"转场_{i:03d}"
                    if not search_term or search_term.lower() in transition_name.lower():
                        effects.append({
                            'id': f'transition_{i}',
                            'name': transition_name,
                            'type': '转场',
                            'excluded': transition_name in self.exclusion_manager.excluded_transitions
                        })

            return {'success': True, 'effects': effects}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def exclude_effects(self, effect_ids):
        """排除特效"""
        try:
            excluded_count = 0

            for effect_id in effect_ids:
                if effect_id.startswith('video_effect_'):
                    effect_name = f"视频特效_{effect_id.split('_')[-1]:03d}"
                    self.exclusion_manager.add_excluded_effect(effect_name)
                    excluded_count += 1
                elif effect_id.startswith('filter_'):
                    filter_name = f"滤镜_{effect_id.split('_')[-1]:03d}"
                    self.exclusion_manager.add_excluded_filter(filter_name)
                    excluded_count += 1
                elif effect_id.startswith('transition_'):
                    transition_name = f"转场_{effect_id.split('_')[-1]:03d}"
                    self.exclusion_manager.add_excluded_transition(transition_name)
                    excluded_count += 1

            # 清除缓存
            self._cache['exclusions'] = None

            return {'success': True, 'excluded_count': excluded_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def include_effects(self, effect_ids):
        """包含特效（移除排除）"""
        try:
            included_count = 0

            for effect_id in effect_ids:
                if effect_id.startswith('video_effect_'):
                    effect_name = f"视频特效_{effect_id.split('_')[-1]:03d}"
                    self.exclusion_manager.remove_excluded_effect(effect_name)
                    included_count += 1
                elif effect_id.startswith('filter_'):
                    filter_name = f"滤镜_{effect_id.split('_')[-1]:03d}"
                    self.exclusion_manager.remove_excluded_filter(filter_name)
                    included_count += 1
                elif effect_id.startswith('transition_'):
                    transition_name = f"转场_{effect_id.split('_')[-1]:03d}"
                    self.exclusion_manager.remove_excluded_transition(transition_name)
                    included_count += 1

            # 清除缓存
            self._cache['exclusions'] = None

            return {'success': True, 'included_count': included_count}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def reset_all_exclusions(self):
        """重置所有排除设置"""
        try:
            # 清空所有排除列表
            self.exclusion_manager.excluded_effects.clear()
            self.exclusion_manager.excluded_filters.clear()
            self.exclusion_manager.excluded_transitions.clear()

            # 清除缓存
            self._cache['exclusions'] = None

            return {'success': True, 'message': '已重置所有排除设置'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_filters(self, search_term, category):
        """搜索滤镜"""
        try:
            filters = []

            # 模拟滤镜数据
            categories = {
                'color': '色彩调整',
                'vintage': '复古风格',
                'modern': '现代风格',
                'artistic': '艺术效果',
                'nature': '自然风光',
                'portrait': '人像美化'
            }

            for i in range(1, 21):  # 显示20个示例
                filter_category = list(categories.keys())[i % len(categories)]
                filter_name = f"滤镜_{i:03d}"

                if category != 'all' and filter_category != category:
                    continue

                if not search_term or search_term.lower() in filter_name.lower():
                    filters.append({
                        'id': f'filter_{i}',
                        'name': filter_name,
                        'category': categories[filter_category],
                        'excluded': filter_name in self.exclusion_manager.excluded_filters
                    })

            return {'success': True, 'filters': filters}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def save_filter_settings(self, min_intensity, max_intensity):
        """保存滤镜设置"""
        try:
            # 保存滤镜强度设置到配置管理器
            success = True
            success &= self.config_manager._set_config_value('filter_intensity_min', min_intensity)
            success &= self.config_manager._set_config_value('filter_intensity_max', max_intensity)

            # 清除缓存
            self._cache['config'] = None

            return {'success': success, 'message': f'滤镜强度设置已保存: {min_intensity}-{max_intensity}%'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_transitions(self, search_term, transition_type):
        """搜索转场"""
        try:
            transitions = []

            # 模拟转场数据
            types = {
                'fade': '淡入淡出',
                'slide': '滑动切换',
                'zoom': '缩放效果',
                'rotate': '旋转切换',
                'wipe': '擦除效果',
                'dissolve': '溶解效果'
            }

            for i in range(1, 21):  # 显示20个示例
                t_type = list(types.keys())[i % len(types)]
                transition_name = f"转场_{i:03d}"

                if transition_type != 'all' and t_type != transition_type:
                    continue

                if not search_term or search_term.lower() in transition_name.lower():
                    transitions.append({
                        'id': f'transition_{i}',
                        'name': transition_name,
                        'type': types[t_type],
                        'excluded': transition_name in self.exclusion_manager.excluded_transitions
                    })

            return {'success': True, 'transitions': transitions}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def save_transition_settings(self, min_duration, max_duration, probability, max_consecutive):
        """保存转场设置"""
        try:
            # 保存转场设置到配置管理器
            success = True
            success &= self.config_manager._set_config_value('transition_min_duration', min_duration)
            success &= self.config_manager._set_config_value('transition_max_duration', max_duration)
            success &= self.config_manager._set_config_value('transition_probability', probability)
            success &= self.config_manager._set_config_value('transition_max_consecutive', max_consecutive)

            # 清除缓存
            self._cache['config'] = None

            return {
                'success': success,
                'message': f'转场设置已保存: 时长{min_duration}-{max_duration}s, 概率{probability}%, 最大连续{max_consecutive}个'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def smart_exclude_effects(self, exclude_type):
        """智能排除特效"""
        try:
            excluded_count = 0
            total_excluded = 0

            if exclude_type == 'exaggerated_effects' or exclude_type == 'all':
                # 模拟排除夸张特效
                exaggerated_effects = [
                    '视频特效_001', '视频特效_003', '视频特效_005',
                    '视频特效_007', '视频特效_009'
                ]
                for effect in exaggerated_effects:
                    if effect not in self.exclusion_manager.excluded_effects:
                        self.exclusion_manager.add_excluded_effect(effect)
                        excluded_count += 1
                        total_excluded += 1

            if exclude_type == 'strong_filters' or exclude_type == 'all':
                # 模拟排除强烈滤镜
                strong_filters = [
                    '滤镜_002', '滤镜_004', '滤镜_006',
                    '滤镜_008', '滤镜_010'
                ]
                for filter_name in strong_filters:
                    if filter_name not in self.exclusion_manager.excluded_filters:
                        self.exclusion_manager.add_excluded_filter(filter_name)
                        excluded_count += 1
                        total_excluded += 1

            if exclude_type == 'fast_transitions' or exclude_type == 'all':
                # 模拟排除快速转场
                fast_transitions = [
                    '转场_001', '转场_003', '转场_005',
                    '转场_007', '转场_009'
                ]
                for transition in fast_transitions:
                    if transition not in self.exclusion_manager.excluded_transitions:
                        self.exclusion_manager.add_excluded_transition(transition)
                        excluded_count += 1
                        total_excluded += 1

            # 清除缓存
            self._cache['exclusions'] = None

            if exclude_type == 'all':
                return {
                    'success': True,
                    'total_excluded': total_excluded,
                    'message': f'全面智能排除完成，共排除 {total_excluded} 个特效'
                }
            else:
                return {
                    'success': True,
                    'excluded_count': excluded_count,
                    'message': f'智能排除完成，共排除 {excluded_count} 个特效'
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_system_status(self):
        """获取系统状态"""
        try:
            import datetime

            # 获取当前时间
            current_time = datetime.datetime.now()

            # 系统基本状态
            system_status = {
                'status': 'running',
                'status_icon': '🟢',
                'status_text': '正常运行',
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # 活跃任务数量
            active_tasks = 0
            if self.automix_status['running']:
                active_tasks = 1

            # 今日完成任务数（真实数据）
            self._reset_daily_statistics_if_needed()
            completed_today = self.task_statistics['completed_today']

            # 错误次数（真实数据）
            error_count = self.task_statistics['error_count_today']

            # 当前操作状态
            current_operation = '空闲中'
            progress = 0
            if self.automix_status['running']:
                current_operation = self.automix_status.get('progress', '处理中...')
                # 简单的进度估算
                if '初始化' in current_operation:
                    progress = 10
                elif '扫描' in current_operation:
                    progress = 20
                elif '选择' in current_operation:
                    progress = 30
                elif '视频' in current_operation:
                    progress = 50
                elif '特效' in current_operation:
                    progress = 70
                elif '音频' in current_operation:
                    progress = 80
                elif '保存' in current_operation:
                    progress = 90
                elif '完成' in current_operation:
                    progress = 100
                else:
                    progress = 50

            return {
                'success': True,
                'system_status': system_status,
                'active_tasks': active_tasks,
                'completed_today': completed_today,
                'error_count': error_count,
                'current_operation': current_operation,
                'progress': progress,
                'logs': self._get_recent_logs()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'system_status': {
                    'status': 'error',
                    'status_icon': '🔴',
                    'status_text': '系统错误'
                },
                'active_tasks': 0,
                'completed_today': 0,
                'error_count': 1
            }



    def _get_recent_logs(self):
        """获取最近的操作日志（模拟实现）"""
        import datetime

        logs = []
        current_time = datetime.datetime.now()

        # 添加当前任务日志
        if self.automix_status['running']:
            logs.append({
                'time': current_time.strftime('%H:%M:%S'),
                'type': 'info',
                'message': self.automix_status.get('progress', '处理中...')
            })

        # 添加系统启动日志
        logs.append({
            'time': (current_time - datetime.timedelta(minutes=5)).strftime('%H:%M:%S'),
            'type': 'success',
            'message': '系统启动完成'
        })

        return logs[-10:]  # 返回最近10条日志

# 创建Flask应用
app = Flask(__name__)
web_interface = OptimizedWebInterface()

@app.route('/')
def index():
    """主页面"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>模板错误</h1><p>错误信息: {str(e)}</p><p>请检查templates/index.html文件是否存在</p>"

@app.route('/test')
def test():
    """测试页面"""
    return "<h1>Flask服务器正常运行</h1><p>这是一个测试页面</p>"

@app.route('/api/config')
def get_config():
    """获取配置信息API"""
    config = web_interface.get_config_info()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置API"""
    config_data = request.get_json()
    result = web_interface.update_config(config_data)
    return jsonify(result)

@app.route('/api/exclusions')
def get_exclusions():
    """获取排除统计API"""
    stats = web_interface.get_exclusion_stats()
    return jsonify(stats)

@app.route('/api/system/status')
def get_system_status():
    """获取系统状态API"""
    try:
        result = web_interface.get_system_status()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products')
def get_products():
    """获取产品列表API"""
    products = web_interface.get_available_products()
    return jsonify(products)

@app.route('/api/status')
def get_status():
    """获取状态信息API"""
    return jsonify(web_interface.automix_status)

@app.route('/api/automix/single', methods=['POST'])
def start_single_automix():
    """启动单个混剪API"""
    try:
        data = request.get_json()
        product = data.get('product')
        duration = data.get('duration', 35)

        if not product:
            return jsonify({'success': False, 'error': '未指定产品'})

        # 启动混剪任务
        result = web_interface.start_single_automix(product, duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/automix/batch', methods=['POST'])
def start_batch_automix():
    """启动批量混剪API"""
    try:
        data = request.get_json()
        product = data.get('product')
        count = data.get('count', 5)
        min_duration = data.get('min_duration', 30)
        max_duration = data.get('max_duration', 40)

        if not product:
            return jsonify({'success': False, 'error': '未指定产品'})

        # 启动批量混剪任务
        result = web_interface.start_batch_automix(product, count, min_duration, max_duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/effects/smart-exclude', methods=['POST'])
def smart_exclude_effects():
    """智能排除特效API"""
    try:
        data = request.get_json()
        exclude_type = data.get('type', 'all')

        result = web_interface.smart_exclude_effects(exclude_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/effects/search', methods=['POST'])
def search_effects():
    """搜索特效API"""
    try:
        data = request.get_json()
        search_term = data.get('search_term', '')
        effect_type = data.get('effect_type', 'all')

        result = web_interface.search_effects(search_term, effect_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/effects/exclude', methods=['POST'])
def exclude_effects():
    """排除特效API"""
    try:
        data = request.get_json()
        effect_ids = data.get('effect_ids', [])

        result = web_interface.exclude_effects(effect_ids)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/effects/include', methods=['POST'])
def include_effects():
    """包含特效API"""
    try:
        data = request.get_json()
        effect_ids = data.get('effect_ids', [])

        result = web_interface.include_effects(effect_ids)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/effects/reset', methods=['POST'])
def reset_effects():
    """重置特效排除API"""
    try:
        result = web_interface.reset_all_exclusions()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/filters/search', methods=['POST'])
def search_filters():
    """搜索滤镜API"""
    try:
        data = request.get_json()
        search_term = data.get('search_term', '')
        category = data.get('category', 'all')

        result = web_interface.search_filters(search_term, category)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/filters/settings', methods=['POST'])
def save_filter_settings():
    """保存滤镜设置API"""
    try:
        data = request.get_json()
        min_intensity = data.get('min_intensity', 15)
        max_intensity = data.get('max_intensity', 25)

        result = web_interface.save_filter_settings(min_intensity, max_intensity)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/transitions/search', methods=['POST'])
def search_transitions():
    """搜索转场API"""
    try:
        data = request.get_json()
        search_term = data.get('search_term', '')
        transition_type = data.get('type', 'all')

        result = web_interface.search_transitions(search_term, transition_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/transitions/settings', methods=['POST'])
def save_transition_settings():
    """保存转场设置API"""
    try:
        data = request.get_json()
        min_duration = data.get('min_duration', 0.5)
        max_duration = data.get('max_duration', 2.0)
        probability = data.get('probability', 80)
        max_consecutive = data.get('max_consecutive', 3)

        result = web_interface.save_transition_settings(min_duration, max_duration, probability, max_consecutive)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def main():
    """主函数"""
    print("🌐 剪映自动混剪工具 - 重构版Web界面")
    print("=" * 50)
    print("🔍 检查依赖包...")
    
    try:
        import flask
        print("✅ 依赖包检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install flask")
        return
    
    print("📁 检查项目结构...")
    
    # 检查必要的目录和文件
    required_paths = [
        'JianYingDraft/core',
        'templates',
        'JianYingDraft/core/configManager.py',
        'JianYingDraft/core/effectExclusionManager.py'
    ]
    
    for path in required_paths:
        if not os.path.exists(path):
            print(f"❌ 缺少必要文件: {path}")
            return
    
    print("✅ 项目结构检查通过")
    print()
    print("🚀 启动Web服务器...")
    print("📱 浏览器访问: http://localhost:5000")
    print("⚙️  功能: 重构版界面，性能优化，一级二级菜单")
    print("🎨 特色: 现代化设计，响应式布局，模块化架构")
    print("🛡️  支持: 轻微特效参数，防审核技术，智能排除")
    print()
    print("💡 使用说明:")
    print("  • 左侧导航: 一级二级菜单结构")
    print("  • 概览页面: 快速操作和统计信息")
    print("  • 配置管理: 分类配置，清晰易用")
    print("  • 特效管理: 智能排除，精确控制")
    print("  • 混剪操作: 单个/批量生成")
    print()
    print("⌨️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 自动打开浏览器
    def open_browser():
        time.sleep(1.5)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 感谢使用剪映自动混剪工具！")

if __name__ == '__main__':
    main()
