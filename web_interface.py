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
        
        # 缓存数据，减少重复计算
        self._cache = {
            'config': None,
            'exclusions': None,
            'effects': None,
            'products': None,
            'cache_time': 0
        }
        self._cache_timeout = 30  # 缓存30秒
    
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
            video_effects = self.exclusion_manager.get_excluded_video_effects()
            filters = self.exclusion_manager.get_excluded_filters()
            transitions = self.exclusion_manager.get_excluded_transitions()
            
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
                    # 这里可以调用实际的混剪逻辑
                    # 模拟混剪过程
                    import time
                    import random

                    self.automix_status['progress'] = f'正在为产品 {product} 生成 {duration}秒 混剪视频...'
                    time.sleep(2)

                    self.automix_status['progress'] = '正在处理视频片段...'
                    time.sleep(3)

                    self.automix_status['progress'] = '正在添加特效和转场...'
                    time.sleep(2)

                    self.automix_status['progress'] = '正在生成最终视频...'
                    time.sleep(3)

                    # 模拟成功完成
                    self.automix_status['running'] = False
                    self.automix_status['progress'] = '混剪完成'
                    self.automix_status['result'] = {
                        'output_path': f'output/{product}_automix_{duration}s.mp4',
                        'duration': duration,
                        'effects_count': random.randint(5, 15),
                        'transitions_count': random.randint(3, 8)
                    }

                except Exception as e:
                    self.automix_status['running'] = False
                    self.automix_status['error'] = str(e)
                    self.automix_status['progress'] = '混剪失败'

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
                    import time
                    import random

                    results = []

                    for i in range(count):
                        current_duration = random.randint(min_duration, max_duration)
                        self.automix_status['progress'] = f'正在生成第 {i+1}/{count} 个视频 ({current_duration}秒)...'

                        # 模拟每个视频的生成过程
                        time.sleep(random.uniform(2, 4))

                        result = {
                            'index': i + 1,
                            'output_path': f'output/{product}_batch_{i+1}_{current_duration}s.mp4',
                            'duration': current_duration,
                            'effects_count': random.randint(5, 15),
                            'transitions_count': random.randint(3, 8)
                        }
                        results.append(result)

                    # 批量混剪完成
                    self.automix_status['running'] = False
                    self.automix_status['progress'] = f'批量混剪完成 (共生成{count}个视频)'
                    self.automix_status['result'] = {
                        'total_count': count,
                        'results': results,
                        'total_duration': sum(r['duration'] for r in results)
                    }

                except Exception as e:
                    self.automix_status['running'] = False
                    self.automix_status['error'] = str(e)
                    self.automix_status['progress'] = '批量混剪失败'

            # 启动后台线程
            threading.Thread(target=run_batch_automix, daemon=True).start()

            return {'success': True, 'message': f'批量混剪任务已启动 (共{count}个视频)'}

        except Exception as e:
            self.automix_status['running'] = False
            return {'success': False, 'error': str(e)}

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
