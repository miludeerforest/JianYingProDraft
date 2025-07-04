"""
剪映自动混剪工具 - Web交互界面
在不改变原有代码的基础上，提供Web浏览器访问界面
"""
import os
import sys
import json
import time
import threading
import webbrowser
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

# 添加项目路径到sys.path
sys.path.append('.')

# 导入原有的核心模块（不修改任何原有代码）
from JianYingDraft.core.configManager import AutoMixConfigManager
from JianYingDraft.core.effectExclusionManager import EffectExclusionManager
from JianYingDraft.core.standardAutoMix import StandardAutoMix

app = Flask(__name__)

class WebInterface:
    """Web界面控制器"""
    
    def __init__(self):
        self.config_manager = AutoMixConfigManager()
        self.exclusion_manager = EffectExclusionManager()
        self.automix_instance = None
        self.automix_status = {
            'running': False,
            'progress': '',
            'error': None,
            'result': None
        }
    
    def get_config_info(self):
        """获取配置信息"""
        try:
            config = {}
            
            # 基础路径配置
            config['material_path'] = self.config_manager.get_material_path()
            config['draft_output_path'] = self.config_manager.get_draft_output_path()
            
            # 视频参数
            min_dur, max_dur = self.config_manager.get_video_duration_range()
            config['video_duration_min'] = min_dur // 1000000
            config['video_duration_max'] = max_dur // 1000000
            config['trim_start_duration'] = self.config_manager.get_trim_start_duration() // 1000000
            config['video_scale_factor'] = self.config_manager.get_video_scale_factor()
            
            # 特效概率
            config['effect_probability'] = self.config_manager.get_effect_probability()
            config['filter_probability'] = self.config_manager.get_filter_probability()
            config['transition_probability'] = self.config_manager.get_transition_probability()
            
            # 滤镜强度
            min_intensity, max_intensity = self.config_manager.get_filter_intensity_range()
            config['filter_intensity_min'] = min_intensity
            config['filter_intensity_max'] = max_intensity
            
            # 音频配置
            narration_vol, background_vol = self.config_manager.get_audio_volumes()
            config['narration_volume'] = narration_vol
            config['background_volume'] = background_vol
            
            # 色彩调整
            (contrast_min, contrast_max), (brightness_min, brightness_max) = self.config_manager.get_color_adjustment_ranges()
            config['contrast_min'] = contrast_min
            config['contrast_max'] = contrast_max
            config['brightness_min'] = brightness_min
            config['brightness_max'] = brightness_max
            
            # 批量生成
            config['batch_count'] = self.config_manager.get_batch_count()
            config['use_vip_effects'] = self.config_manager.get_use_vip_effects()
            
            # 防审核配置
            config['pexels_overlay_enabled'] = self.config_manager.is_pexels_overlay_enabled()
            config['pexels_overlay_opacity'] = self.config_manager.get_pexels_overlay_opacity()
            
            return config
        except Exception as e:
            return {'error': str(e)}
    
    def get_exclusion_stats(self):
        """获取排除统计信息"""
        try:
            stats = {}
            
            # 滤镜统计
            all_filters = self.exclusion_manager.metadata_manager.get_available_filters()
            available_filters = self.exclusion_manager.get_filtered_filters()
            stats['filters'] = {
                'total': len(all_filters),
                'excluded': len(self.exclusion_manager.excluded_filters),
                'available': len(available_filters),
                'excluded_list': list(self.exclusion_manager.excluded_filters)
            }
            
            # 特效统计
            all_effects = self.exclusion_manager.metadata_manager.get_available_effects()
            available_effects = self.exclusion_manager.get_filtered_effects()
            stats['effects'] = {
                'total': len(all_effects),
                'excluded': len(self.exclusion_manager.excluded_effects),
                'available': len(available_effects),
                'excluded_list': list(self.exclusion_manager.excluded_effects)
            }
            
            # 转场统计
            all_transitions = self.exclusion_manager.metadata_manager.get_available_transitions()
            available_transitions = self.exclusion_manager.get_filtered_transitions()
            stats['transitions'] = {
                'total': len(all_transitions),
                'excluded': len(self.exclusion_manager.excluded_transitions),
                'available': len(available_transitions),
                'excluded_list': list(self.exclusion_manager.excluded_transitions)
            }
            
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
                    elif key == 'effect_probability':
                        success &= self.config_manager._set_config_value('effect_probability', float(value))
                    elif key == 'filter_probability':
                        success &= self.config_manager._set_config_value('filter_probability', float(value))
                    elif key == 'transition_probability':
                        success &= self.config_manager._set_config_value('transition_probability', float(value))
                    elif key == 'filter_intensity_min':
                        success &= self.config_manager._set_config_value('filter_intensity_min', int(value))
                    elif key == 'filter_intensity_max':
                        success &= self.config_manager._set_config_value('filter_intensity_max', int(value))
                    elif key == 'narration_volume':
                        success &= self.config_manager._set_config_value('narration_volume', float(value))
                    elif key == 'background_volume':
                        success &= self.config_manager._set_config_value('background_volume', float(value))
                    elif key == 'batch_count':
                        success &= self.config_manager._set_config_value('batch_count', int(value))
                    elif key == 'use_vip_effects':
                        success &= self.config_manager._set_config_value('use_vip_effects', bool(value))
                    elif key == 'pexels_overlay_enabled':
                        success &= self.config_manager._set_config_value('enable_pexels_overlay', bool(value))
                    elif key == 'pexels_overlay_opacity':
                        success &= self.config_manager._set_config_value('pexels_overlay_opacity', float(value))
                except Exception as e:
                    errors.append(f"{key}: {str(e)}")
            
            return {'success': success, 'errors': errors}
        except Exception as e:
            return {'success': False, 'errors': [str(e)]}
    
    def start_automix(self, product_name=None):
        """启动自动混剪（异步）"""
        if self.automix_status['running']:
            return {'success': False, 'message': '混剪正在进行中'}
        
        def run_automix():
            try:
                self.automix_status['running'] = True
                self.automix_status['progress'] = '正在初始化...'
                self.automix_status['error'] = None
                self.automix_status['result'] = None
                
                # 创建StandardAutoMix实例
                draft_name = f"WebAutoMix_{int(time.time())}"
                self.automix_instance = StandardAutoMix(draft_name)
                
                self.automix_status['progress'] = '正在扫描素材...'
                
                # 执行混剪
                # 获取目标时长（默认35秒）
                target_duration = 35000000  # 35秒，单位微秒

                # 调用正确的方法
                result = self.automix_instance.auto_mix(
                    target_duration=target_duration,
                    product_model=product_name
                )
                
                self.automix_status['progress'] = '混剪完成'
                self.automix_status['result'] = result
                
            except Exception as e:
                self.automix_status['error'] = str(e)
                self.automix_status['progress'] = f'错误: {str(e)}'
            finally:
                self.automix_status['running'] = False
        
        # 在新线程中运行
        thread = threading.Thread(target=run_automix)
        thread.daemon = True
        thread.start()
        
        return {'success': True, 'message': '混剪已开始'}
    
    def get_automix_status(self):
        """获取混剪状态"""
        return self.automix_status
    
    def get_available_products(self):
        """获取可用产品列表"""
        try:
            # 直接从配置管理器获取素材路径并扫描产品目录
            material_path = self.config_manager.get_material_path()
            if not os.path.exists(material_path):
                return {'success': False, 'error': '素材库路径不存在'}

            products = []
            for item in os.listdir(material_path):
                item_path = os.path.join(material_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    products.append(item)

            return {'success': True, 'products': sorted(products)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# 创建Web界面实例
web_interface = WebInterface()

# Web路由定义
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/config')
def get_config():
    """获取配置信息API"""
    config = web_interface.get_config_info()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置API"""
    config_data = request.json
    result = web_interface.update_config(config_data)
    return jsonify(result)

@app.route('/api/exclusions')
def get_exclusions():
    """获取排除统计API"""
    stats = web_interface.get_exclusion_stats()
    return jsonify(stats)

@app.route('/api/exclusions/<effect_type>/<action>', methods=['POST'])
def manage_exclusions(effect_type, action):
    """管理排除列表API"""
    data = request.json
    effect_name = data.get('name', '')
    
    try:
        if effect_type == 'filters':
            if action == 'add':
                result = web_interface.exclusion_manager.add_excluded_filter(effect_name)
            elif action == 'remove':
                result = web_interface.exclusion_manager.remove_excluded_filter(effect_name)
        elif effect_type == 'effects':
            if action == 'add':
                result = web_interface.exclusion_manager.add_excluded_effect(effect_name)
            elif action == 'remove':
                result = web_interface.exclusion_manager.remove_excluded_effect(effect_name)
        elif effect_type == 'transitions':
            if action == 'add':
                result = web_interface.exclusion_manager.add_excluded_transition(effect_name)
            elif action == 'remove':
                result = web_interface.exclusion_manager.remove_excluded_transition(effect_name)
        else:
            return jsonify({'success': False, 'error': '无效的效果类型'})
        
        return jsonify({'success': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products')
def get_products():
    """获取可用产品列表API"""
    result = web_interface.get_available_products()
    return jsonify(result)

@app.route('/api/automix/start', methods=['POST'])
def start_automix():
    """启动自动混剪API"""
    data = request.json or {}
    product_name = data.get('product_name')
    result = web_interface.start_automix(product_name)
    return jsonify(result)

@app.route('/api/automix/status')
def get_automix_status():
    """获取混剪状态API"""
    status = web_interface.get_automix_status()
    return jsonify(status)

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🌐 剪映自动混剪工具 - Web界面")
    print("=" * 50)
    print("🚀 启动Web服务器...")
    print("📱 浏览器访问: http://localhost:5000")
    print("⚙️  功能: 配置管理、排除设置、自动混剪")
    print("🔧 基于原有代码，无任何修改")
    
    # 自动打开浏览器
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5000')).start()
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=False)
