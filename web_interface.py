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
import subprocess
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
            
            # 音频设置
            config['narration_volume'] = self.config_manager.get_narration_volume()
            config['background_volume'] = self.config_manager.get_background_volume()
            
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
                    '泰语字幕乱码修复'
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

                # 获取批量生成数量
                batch_count = self.config_manager.get_batch_count()

                # 获取目标时长范围
                min_duration = self.config_manager.get_video_duration_min()
                max_duration = self.config_manager.get_video_duration_max()

                self.automix_status['progress'] = f'开始批量生成 {batch_count} 个视频...'

                results = []
                import random

                for i in range(batch_count):
                    try:
                        self.automix_status['progress'] = f'正在生成第 {i+1}/{batch_count} 个视频...'

                        # 随机选择时长
                        target_duration = random.randint(min_duration, max_duration)

                        # 创建StandardAutoMix实例
                        draft_name = f"WebAutoMix_{int(time.time())}_{i+1}"
                        self.automix_instance = StandardAutoMix(draft_name)

                        # 执行混剪
                        result = self.automix_instance.auto_mix(
                            target_duration=target_duration,
                            product_model=product_name
                        )

                        results.append({
                            'success': True,
                            'draft_name': draft_name,
                            'duration': target_duration,
                            'result': result
                        })

                    except Exception as e:
                        results.append({
                            'success': False,
                            'draft_name': f"WebAutoMix_{int(time.time())}_{i+1}",
                            'error': str(e)
                        })

                # 统计结果
                success_count = sum(1 for r in results if r['success'])
                self.automix_status['progress'] = f'批量生成完成！成功: {success_count}/{batch_count}'
                self.automix_status['result'] = {
                    'batch_results': results,
                    'success_count': success_count,
                    'total_count': batch_count
                }

            except Exception as e:
                self.automix_status['error'] = str(e)
                self.automix_status['progress'] = f'错误: {str(e)}'
            finally:
                self.automix_status['running'] = False

        # 在新线程中运行
        thread = threading.Thread(target=run_automix)
        thread.daemon = True
        thread.start()

        return {'success': True, 'message': '批量混剪已开始'}
    
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

    def get_available_effects_list(self, effect_type='all'):
        """获取可用特效列表"""
        try:
            result = {}

            if effect_type in ['all', 'filters']:
                all_filters = self.exclusion_manager.metadata_manager.get_available_filters()
                available_filters = [f.name for f in all_filters if f.name not in self.exclusion_manager.excluded_filters]
                result['filters'] = sorted(available_filters)

            if effect_type in ['all', 'effects']:
                all_effects = self.exclusion_manager.metadata_manager.get_available_effects()
                available_effects = [e.name for e in all_effects if e.name not in self.exclusion_manager.excluded_effects]
                result['effects'] = sorted(available_effects)

            if effect_type in ['all', 'transitions']:
                all_transitions = self.exclusion_manager.metadata_manager.get_available_transitions()
                available_transitions = [t.name for t in all_transitions if t.name not in self.exclusion_manager.excluded_transitions]
                result['transitions'] = sorted(available_transitions)

            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def smart_exclude_exaggerated_effects(self):
        """智能排除夸张特效"""
        try:
            # 获取预览
            preview = self.exclusion_manager.get_exaggerated_effects_preview()

            # 执行排除
            excluded_count = self.exclusion_manager.auto_exclude_exaggerated_effects()

            return {
                'success': True,
                'preview': preview,
                'excluded_count': excluded_count
            }
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

@app.route('/api/effects/available')
def get_available_effects():
    """获取可用特效列表API"""
    effect_type = request.args.get('type', 'all')
    result = web_interface.get_available_effects_list(effect_type)
    return jsonify(result)

@app.route('/api/exclusions/smart-exclude', methods=['POST'])
def smart_exclude():
    """智能排除夸张特效API"""
    result = web_interface.smart_exclude_exaggerated_effects()
    return jsonify(result)

# 创建Web界面实例
web_interface = WebInterface()

def create_app():
    """创建Flask应用实例（用于生产部署）"""
    return app

def check_dependencies():
    """检查依赖包"""
    required_packages = ['flask']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ 缺少依赖包:", ', '.join(missing_packages))
        print("📦 请安装依赖包:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    return True

def check_project_structure():
    """检查项目结构"""
    required_files = [
        'JianYingDraft/core/configManager.py',
        'JianYingDraft/core/effectExclusionManager.py',
        'JianYingDraft/core/standardAutoMix.py',
        'templates/index.html'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("❌ 缺少必要文件:")
        for file_path in missing_files:
            print(f"   {file_path}")
        return False

    return True

def start_web_interface():
    """启动Web界面的主函数"""
    print("🌐 剪映自动混剪工具 - Web界面")
    print("=" * 50)

    # 检查依赖
    print("🔍 检查依赖包...")
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的包后重试")
        return False
    print("✅ 依赖包检查通过")

    # 检查项目结构
    print("📁 检查项目结构...")
    if not check_project_structure():
        print("\n❌ 项目结构检查失败，请确保在正确的项目目录中运行")
        return False
    print("✅ 项目结构检查通过")

    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 已创建templates目录")

    print("\n🚀 启动Web服务器...")
    print("📱 浏览器访问: http://localhost:5000")
    print("⚙️  功能: 配置管理、排除设置、自动混剪、高级防审核技术")
    print("🔧 基于原有代码，无任何修改")
    print("🛡️  支持100%强制执行防审核技术")
    print("\n💡 使用说明:")
    print("  • 配置管理: 设置素材路径、输出路径等")
    print("  • 特效排除: 管理不需要的特效、滤镜、转场")
    print("  • 自动混剪: 一键生成视频草稿")
    print("  • 高级防审核: 镜像翻转、模糊背景、抽帧处理")
    print("  • 强制执行: 一键设置100%执行模式")
    print("\n⌨️  按 Ctrl+C 停止服务器")
    print("-" * 50)

    # 自动打开浏览器
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open('http://localhost:5000')
            print("🌐 已自动打开浏览器")
        except:
            print("⚠️  无法自动打开浏览器，请手动访问 http://localhost:5000")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # 启动Flask应用
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Web服务器已停止")
        print("感谢使用剪映自动混剪工具！")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False

    return True

if __name__ == '__main__':
    start_web_interface()
