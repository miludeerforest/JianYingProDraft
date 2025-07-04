#!/usr/bin/env python3
"""
剪映自动混剪 - 终端交互式工具
支持产品视频的智能混剪，包含特效、滤镜、转场、字幕等功能
"""
import sys
import os
import time
from typing import Optional, Dict, Any

# 添加项目路径
sys.path.append('.')

from JianYingDraft.core.standardAutoMix import StandardAutoMix
from JianYingDraft.core.configManager import AutoMixConfigManager
from JianYingDraft.core.effectExclusionManager import EffectExclusionManager
import json


class InteractiveAutoMix:
    """交互式自动混剪工具"""
    
    def __init__(self):
        self.config_manager = AutoMixConfigManager
        self.current_draft = None
        self.exclusion_manager = EffectExclusionManager()
        
    def show_banner(self):
        """显示欢迎横幅"""
        print("=" * 60)
        print("🎬 剪映自动混剪工具 - 交互式版本")
        print("=" * 60)
        print("✨ 功能特色:")
        print("  📱 9:16竖屏格式")
        print("  🎯 智能素材选择")
        print("  🔇 视频自动静音")
        print("  ✨ 随机特效滤镜")
        print("  🔄 自动转场效果")
        print("  📝 SRT字幕支持")
        print("  🎵 双音频轨道")
        print("  📁 子文件夹全覆盖")
        print("=" * 60)
        
    def show_main_menu(self):
        """显示主菜单"""
        print("\n📋 主菜单:")
        print("1. 🎬 自动混剪")
        print("2. 📊 批量生成")
        print("3. 🚫 特效排除管理")
        print("4. 🛡️  Pexels防审核设置")
        print("5. ⚙️  查看配置信息")
        print("6. 🔧 修改配置")
        print("7. ❓ 帮助信息")
        print("0. 🚪 退出程序")
        print("-" * 40)
        print("💡 使用标准化引擎，包含VIP资源、弹幕过滤、100%覆盖率等所有优化")

    def get_user_input(self, prompt: str, default: str = None, input_type: type = str):
        """获取用户输入"""
        if default:
            full_prompt = f"{prompt} (默认: {default}): "
        else:
            full_prompt = f"{prompt}: "
            
        while True:
            try:
                user_input = input(full_prompt).strip()
                
                if not user_input and default is not None:
                    return input_type(default)
                elif not user_input:
                    print("❌ 输入不能为空，请重新输入")
                    continue
                    
                return input_type(user_input)
            except ValueError:
                print(f"❌ 输入格式错误，请输入{input_type.__name__}类型")
            except KeyboardInterrupt:
                print("\n\n👋 用户取消操作")
                return None
                
    def show_config_info(self):
        """显示配置信息"""
        print("\n⚙️  当前配置信息:")
        print("=" * 60)

        try:
            # 基础路径配置
            print("📁 路径配置:")
            print(f"  素材库路径: {self.config_manager.get_material_path()}")
            print(f"  草稿输出路径: {self.config_manager.get_draft_output_path()}")

            # 视频参数配置
            print("\n🎬 视频参数:")
            min_dur, max_dur = self.config_manager.get_video_duration_range()
            print(f"  视频时长范围: {min_dur//1000000}s - {max_dur//1000000}s")
            print(f"  视频去前时长: {self.config_manager.get_trim_start_duration()//1000000}秒")
            print(f"  画面缩放比例: {self.config_manager.get_video_scale_factor():.0%}")

            # 特效概率配置
            print("\n🎨 特效概率:")
            print(f"  特效应用概率: {self.config_manager.get_effect_probability():.0%}")
            print(f"  滤镜应用概率: {self.config_manager.get_filter_probability():.0%}")
            print(f"  转场应用概率: {self.config_manager.get_transition_probability():.0%}")

            # 滤镜强度配置
            min_intensity, max_intensity = self.config_manager.get_filter_intensity_range()
            print(f"  滤镜强度范围: {min_intensity}% - {max_intensity}%")

            # 音频配置
            print("\n🎵 音频配置:")
            narration_vol, background_vol = self.config_manager.get_audio_volumes()
            print(f"  解说音量: {narration_vol:.0%}")
            print(f"  背景音量: {background_vol:.0%}")

            # 色彩调整配置
            print("\n🌈 色彩调整:")
            (contrast_min, contrast_max), (brightness_min, brightness_max) = self.config_manager.get_color_adjustment_ranges()
            print(f"  对比度范围: {contrast_min:.1f} - {contrast_max:.1f}")
            print(f"  亮度范围: {brightness_min:.1f} - {brightness_max:.1f}")

            # 批量生成配置
            print("\n📦 批量生成:")
            print(f"  批量生成数量: {self.config_manager.get_batch_count()}")
            print(f"  使用VIP特效: {'是' if self.config_manager.get_use_vip_effects() else '否'}")

            # Pexels防审核配置
            print("\n🛡️  防审核配置:")
            print(f"  Pexels覆盖层: {'启用' if self.config_manager.is_pexels_overlay_enabled() else '禁用'}")
            print(f"  覆盖层不透明度: {self.config_manager.get_pexels_overlay_opacity():.1%}")
            print(f"  API密钥状态: {'已配置' if self.config_manager.get_pexels_api_key() else '未配置'}")

            # 时长过滤配置
            print("\n⏱️  时长过滤:")
            min_filter_dur, max_filter_dur = self.config_manager.get_video_duration_filter_range()
            print(f"  最小视频时长: {min_filter_dur//1000000}秒")
            print(f"  最大视频时长: {max_filter_dur//1000000}秒")

        except Exception as e:
            print(f"❌ 读取配置失败: {str(e)}")

        print("=" * 60)

    def modify_config(self):
        """修改配置"""
        while True:
            print("\n🔧 配置修改")
            print("=" * 60)
            print("📋 可修改的配置项:")
            print("1. 📁 素材库路径")
            print("2. 💾 草稿输出路径")
            print("3. ⏱️  视频时长范围")
            print("4. 🎨 特效概率设置")
            print("5. 🎵 音频音量设置")
            print("6. 🌈 色彩调整范围")
            print("7. 📦 批量生成设置")
            print("8. 🛡️  防审核设置")
            print("9. ⚙️  高级设置")
            print("0. 🔙 返回主菜单")
            print("-" * 40)

            try:
                choice = int(input("请选择要修改的配置项 (默认: 0): ") or "0")

                if choice == 0:
                    break
                elif choice == 1:
                    self.modify_paths()
                elif choice == 2:
                    self.modify_draft_path()
                elif choice == 3:
                    self.modify_video_duration()
                elif choice == 4:
                    self.modify_effect_probabilities()
                elif choice == 5:
                    self.modify_audio_volumes()
                elif choice == 6:
                    self.modify_color_adjustment()
                elif choice == 7:
                    self.modify_batch_settings()
                elif choice == 8:
                    self.modify_pexels_settings()
                elif choice == 9:
                    self.modify_advanced_settings()
                else:
                    print("❌ 无效选择，请重新输入")

            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                print("\n👋 操作已取消")
                break

            if choice != 0:
                input("\n按回车键继续...")

    def modify_paths(self):
        """修改素材库路径"""
        print("\n📁 修改素材库路径")
        print("-" * 40)

        current_path = self.config_manager.get_material_path()
        print(f"当前路径: {current_path}")

        new_path = input("请输入新的素材库路径 (留空保持不变): ").strip()
        if not new_path:
            print("⚠️  路径未修改")
            return

        # 验证路径
        if not os.path.exists(new_path):
            print(f"❌ 路径不存在: {new_path}")
            create = input("是否创建该路径? (y/N): ").strip().lower()
            if create == 'y':
                try:
                    os.makedirs(new_path, exist_ok=True)
                    print(f"✅ 已创建路径: {new_path}")
                except Exception as e:
                    print(f"❌ 创建路径失败: {str(e)}")
                    return
            else:
                return

        # 保存配置
        if self.config_manager._set_config_value('material_path', new_path):
            print(f"✅ 素材库路径已更新: {new_path}")
        else:
            print("❌ 保存配置失败")

    def modify_draft_path(self):
        """修改草稿输出路径"""
        print("\n💾 修改草稿输出路径")
        print("-" * 40)

        current_path = self.config_manager.get_draft_output_path()
        print(f"当前路径: {current_path}")

        new_path = input("请输入新的草稿输出路径 (留空保持不变): ").strip()
        if not new_path:
            print("⚠️  路径未修改")
            return

        # 验证路径
        if not os.path.exists(new_path):
            print(f"❌ 路径不存在: {new_path}")
            create = input("是否创建该路径? (y/N): ").strip().lower()
            if create == 'y':
                try:
                    os.makedirs(new_path, exist_ok=True)
                    print(f"✅ 已创建路径: {new_path}")
                except Exception as e:
                    print(f"❌ 创建路径失败: {str(e)}")
                    return
            else:
                return

        # 保存配置
        if self.config_manager._set_config_value('draft_output_path', new_path):
            print(f"✅ 草稿输出路径已更新: {new_path}")
        else:
            print("❌ 保存配置失败")

    def modify_video_duration(self):
        """修改视频时长范围"""
        print("\n⏱️  修改视频时长范围")
        print("-" * 40)

        min_dur, max_dur = self.config_manager.get_video_duration_range()
        print(f"当前时长范围: {min_dur//1000000}s - {max_dur//1000000}s")

        try:
            min_input = input(f"请输入最小时长(秒) (当前: {min_dur//1000000}, 留空保持不变): ").strip()
            max_input = input(f"请输入最大时长(秒) (当前: {max_dur//1000000}, 留空保持不变): ").strip()

            new_min = int(min_input) * 1000000 if min_input else min_dur
            new_max = int(max_input) * 1000000 if max_input else max_dur

            # 验证范围
            if new_min >= new_max:
                print("❌ 最小时长必须小于最大时长")
                return
            if new_min < 5000000:  # 5秒
                print("❌ 最小时长不能小于5秒")
                return
            if new_max > 300000000:  # 300秒
                print("❌ 最大时长不能超过300秒")
                return

            # 保存配置
            success = True
            if new_min != min_dur:
                success &= self.config_manager._set_config_value('video_duration_min', new_min)
            if new_max != max_dur:
                success &= self.config_manager._set_config_value('video_duration_max', new_max)

            if success:
                print(f"✅ 视频时长范围已更新: {new_min//1000000}s - {new_max//1000000}s")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def modify_effect_probabilities(self):
        """修改特效概率设置"""
        print("\n🎨 修改特效概率设置")
        print("-" * 40)

        current_effect = self.config_manager.get_effect_probability()
        current_filter = self.config_manager.get_filter_probability()
        current_transition = self.config_manager.get_transition_probability()

        print(f"当前设置:")
        print(f"  特效概率: {current_effect:.0%}")
        print(f"  滤镜概率: {current_filter:.0%}")
        print(f"  转场概率: {current_transition:.0%}")

        try:
            effect_input = input(f"请输入特效概率(0-100) (当前: {current_effect:.0%}, 留空保持不变): ").strip()
            filter_input = input(f"请输入滤镜概率(0-100) (当前: {current_filter:.0%}, 留空保持不变): ").strip()
            transition_input = input(f"请输入转场概率(0-100) (当前: {current_transition:.0%}, 留空保持不变): ").strip()

            success = True

            if effect_input:
                effect_prob = float(effect_input) / 100
                if 0 <= effect_prob <= 1:
                    success &= self.config_manager._set_config_value('effect_probability', effect_prob)
                else:
                    print("❌ 特效概率必须在0-100之间")
                    return

            if filter_input:
                filter_prob = float(filter_input) / 100
                if 0 <= filter_prob <= 1:
                    success &= self.config_manager._set_config_value('filter_probability', filter_prob)
                else:
                    print("❌ 滤镜概率必须在0-100之间")
                    return

            if transition_input:
                transition_prob = float(transition_input) / 100
                if 0 <= transition_prob <= 1:
                    success &= self.config_manager._set_config_value('transition_probability', transition_prob)
                else:
                    print("❌ 转场概率必须在0-100之间")
                    return

            if success:
                print("✅ 特效概率设置已更新")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def modify_audio_volumes(self):
        """修改音频音量设置"""
        print("\n🎵 修改音频音量设置")
        print("-" * 40)

        narration_vol, background_vol = self.config_manager.get_audio_volumes()
        print(f"当前设置:")
        print(f"  解说音量: {narration_vol:.0%}")
        print(f"  背景音量: {background_vol:.0%}")

        try:
            narration_input = input(f"请输入解说音量(0-100) (当前: {narration_vol:.0%}, 留空保持不变): ").strip()
            background_input = input(f"请输入背景音量(0-100) (当前: {background_vol:.0%}, 留空保持不变): ").strip()

            success = True

            if narration_input:
                narration_volume = float(narration_input) / 100
                if 0 <= narration_volume <= 1:
                    success &= self.config_manager._set_config_value('narration_volume', narration_volume)
                else:
                    print("❌ 解说音量必须在0-100之间")
                    return

            if background_input:
                background_volume = float(background_input) / 100
                if 0 <= background_volume <= 1:
                    success &= self.config_manager._set_config_value('background_volume', background_volume)
                else:
                    print("❌ 背景音量必须在0-100之间")
                    return

            if success:
                print("✅ 音频音量设置已更新")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def modify_color_adjustment(self):
        """修改色彩调整范围"""
        print("\n🌈 修改色彩调整范围")
        print("-" * 40)

        (contrast_min, contrast_max), (brightness_min, brightness_max) = self.config_manager.get_color_adjustment_ranges()
        print(f"当前设置:")
        print(f"  对比度范围: {contrast_min:.1f} - {contrast_max:.1f}")
        print(f"  亮度范围: {brightness_min:.1f} - {brightness_max:.1f}")

        try:
            print("\n对比度设置:")
            contrast_min_input = input(f"请输入对比度最小值(0.1-2.0) (当前: {contrast_min:.1f}, 留空保持不变): ").strip()
            contrast_max_input = input(f"请输入对比度最大值(0.1-2.0) (当前: {contrast_max:.1f}, 留空保持不变): ").strip()

            print("\n亮度设置:")
            brightness_min_input = input(f"请输入亮度最小值(0.1-2.0) (当前: {brightness_min:.1f}, 留空保持不变): ").strip()
            brightness_max_input = input(f"请输入亮度最大值(0.1-2.0) (当前: {brightness_max:.1f}, 留空保持不变): ").strip()

            success = True

            # 处理对比度设置
            new_contrast_min = float(contrast_min_input) if contrast_min_input else contrast_min
            new_contrast_max = float(contrast_max_input) if contrast_max_input else contrast_max

            if contrast_min_input or contrast_max_input:
                if new_contrast_min >= new_contrast_max:
                    print("❌ 对比度最小值必须小于最大值")
                    return
                if not (0.1 <= new_contrast_min <= 2.0) or not (0.1 <= new_contrast_max <= 2.0):
                    print("❌ 对比度值必须在0.1-2.0之间")
                    return

                success &= self.config_manager._set_config_value('contrast_range_min', new_contrast_min)
                success &= self.config_manager._set_config_value('contrast_range_max', new_contrast_max)

            # 处理亮度设置
            new_brightness_min = float(brightness_min_input) if brightness_min_input else brightness_min
            new_brightness_max = float(brightness_max_input) if brightness_max_input else brightness_max

            if brightness_min_input or brightness_max_input:
                if new_brightness_min >= new_brightness_max:
                    print("❌ 亮度最小值必须小于最大值")
                    return
                if not (0.1 <= new_brightness_min <= 2.0) or not (0.1 <= new_brightness_max <= 2.0):
                    print("❌ 亮度值必须在0.1-2.0之间")
                    return

                success &= self.config_manager._set_config_value('brightness_range_min', new_brightness_min)
                success &= self.config_manager._set_config_value('brightness_range_max', new_brightness_max)

            if success:
                print("✅ 色彩调整范围已更新")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def modify_batch_settings(self):
        """修改批量生成设置"""
        print("\n📦 修改批量生成设置")
        print("-" * 40)

        current_batch = self.config_manager.get_batch_count()
        current_vip = self.config_manager.get_use_vip_effects()

        print(f"当前设置:")
        print(f"  批量生成数量: {current_batch}")
        print(f"  使用VIP特效: {'是' if current_vip else '否'}")

        try:
            batch_input = input(f"请输入批量生成数量(1-100) (当前: {current_batch}, 留空保持不变): ").strip()
            vip_input = input(f"是否使用VIP特效? (y/n) (当前: {'y' if current_vip else 'n'}, 留空保持不变): ").strip().lower()

            success = True

            if batch_input:
                batch_count = int(batch_input)
                if 1 <= batch_count <= 100:
                    success &= self.config_manager._set_config_value('batch_count', batch_count)
                else:
                    print("❌ 批量生成数量必须在1-100之间")
                    return

            if vip_input:
                if vip_input in ['y', 'yes', '1', 'true']:
                    success &= self.config_manager._set_config_value('use_vip_effects', True)
                elif vip_input in ['n', 'no', '0', 'false']:
                    success &= self.config_manager._set_config_value('use_vip_effects', False)
                else:
                    print("❌ 请输入 y 或 n")
                    return

            if success:
                print("✅ 批量生成设置已更新")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def modify_pexels_settings(self):
        """修改防审核设置"""
        print("\n🛡️  修改防审核设置")
        print("-" * 40)

        current_enabled = self.config_manager.is_pexels_overlay_enabled()
        current_opacity = self.config_manager.get_pexels_overlay_opacity()

        print(f"当前设置:")
        print(f"  Pexels覆盖层: {'启用' if current_enabled else '禁用'}")
        print(f"  覆盖层不透明度: {current_opacity:.1%}")

        try:
            enabled_input = input(f"是否启用Pexels覆盖层? (y/n) (当前: {'y' if current_enabled else 'n'}, 留空保持不变): ").strip().lower()
            opacity_input = input(f"请输入覆盖层不透明度(1-20) (当前: {current_opacity*100:.0f}%, 留空保持不变): ").strip()

            success = True

            if enabled_input:
                if enabled_input in ['y', 'yes', '1', 'true']:
                    success &= self.config_manager._set_config_value('enable_pexels_overlay', True)
                elif enabled_input in ['n', 'no', '0', 'false']:
                    success &= self.config_manager._set_config_value('enable_pexels_overlay', False)
                else:
                    print("❌ 请输入 y 或 n")
                    return

            if opacity_input:
                opacity = float(opacity_input) / 100
                if 0.01 <= opacity <= 0.2:  # 1%-20%
                    success &= self.config_manager._set_config_value('pexels_overlay_opacity', opacity)
                else:
                    print("❌ 不透明度必须在1-20%之间")
                    return

            if success:
                print("✅ 防审核设置已更新")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def modify_advanced_settings(self):
        """修改高级设置"""
        print("\n⚙️  修改高级设置")
        print("-" * 40)

        current_scale = self.config_manager.get_video_scale_factor()
        current_trim = self.config_manager.get_trim_start_duration()
        min_intensity, max_intensity = self.config_manager.get_filter_intensity_range()

        print(f"当前设置:")
        print(f"  视频缩放比例: {current_scale:.0%}")
        print(f"  视频去前时长: {current_trim//1000000}秒")
        print(f"  滤镜强度范围: {min_intensity}% - {max_intensity}%")

        try:
            scale_input = input(f"请输入视频缩放比例(50-200) (当前: {current_scale:.0%}, 留空保持不变): ").strip()
            trim_input = input(f"请输入视频去前时长(0-10秒) (当前: {current_trim//1000000}秒, 留空保持不变): ").strip()

            print("\n滤镜强度设置:")
            intensity_min_input = input(f"请输入滤镜强度最小值(1-50) (当前: {min_intensity}%, 留空保持不变): ").strip()
            intensity_max_input = input(f"请输入滤镜强度最大值(1-50) (当前: {max_intensity}%, 留空保持不变): ").strip()

            success = True

            if scale_input:
                scale_factor = float(scale_input) / 100
                if 0.5 <= scale_factor <= 2.0:
                    success &= self.config_manager._set_config_value('video_scale_factor', scale_factor)
                else:
                    print("❌ 缩放比例必须在50-200%之间")
                    return

            if trim_input:
                trim_duration = int(trim_input) * 1000000
                if 0 <= trim_duration <= 10000000:  # 0-10秒
                    success &= self.config_manager._set_config_value('trim_start_duration', trim_duration)
                else:
                    print("❌ 去前时长必须在0-10秒之间")
                    return

            # 处理滤镜强度设置
            new_min_intensity = int(intensity_min_input) if intensity_min_input else min_intensity
            new_max_intensity = int(intensity_max_input) if intensity_max_input else max_intensity

            if intensity_min_input or intensity_max_input:
                if new_min_intensity >= new_max_intensity:
                    print("❌ 滤镜强度最小值必须小于最大值")
                    return
                if not (1 <= new_min_intensity <= 50) or not (1 <= new_max_intensity <= 50):
                    print("❌ 滤镜强度必须在1-50%之间")
                    return

                success &= self.config_manager._set_config_value('filter_intensity_min', new_min_intensity)
                success &= self.config_manager._set_config_value('filter_intensity_max', new_max_intensity)

            if success:
                print("✅ 高级设置已更新")
            else:
                print("❌ 保存配置失败")

        except ValueError:
            print("❌ 请输入有效的数字")

    def get_available_products(self) -> list:
        """获取可用的产品型号"""
        try:
            material_path = self.config_manager.get_material_path()
            if not os.path.exists(material_path):
                return []
                
            products = []
            for item in os.listdir(material_path):
                item_path = os.path.join(material_path, item)
                if os.path.isdir(item_path):
                    products.append(item)
            return sorted(products)
        except Exception:
            return []
            
    def select_product_model(self) -> Optional[str]:
        """选择产品型号"""
        products = self.get_available_products()
        
        if not products:
            print("❌ 未找到可用的产品型号")
            return None
            
        print("\n📦 可用产品型号:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product}")
        print("0. 随机选择")
        
        while True:
            choice = self.get_user_input("请选择产品型号", "0", int)
            if choice is None:
                return None
            elif choice == 0:
                return None  # 随机选择
            elif 1 <= choice <= len(products):
                return products[choice - 1]
            else:
                print(f"❌ 请输入1-{len(products)}之间的数字")
                
    def progress_callback(self, message: str, progress: float):
        """进度回调函数"""
        if progress >= 0:
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"\r[{bar}] {progress:.1%} {message}", end="", flush=True)
        else:
            print(f"\n❌ {message}")
            
    def start_standard_auto_mix(self):
        """开始自动混剪"""
        print("\n🎬 自动混剪")
        print("-" * 40)
        print("✨ 功能特色:")
        print("  🎨 完整VIP资源库 (468种滤镜、912种特效、362种转场)")
        print("  🚫 排除弹幕类转场 (专业视觉过渡)")
        print("  💯 100%覆盖率保证 (滤镜、特效、转场)")
        print("  🔧 兼容性改进 (稳定可靠)")
        print("  📱 9:16竖屏优化")
        print("  🚫 支持特效排除管理")
        print("-" * 40)

        # 获取草稿名称
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        default_name = f"AutoMix_{timestamp}"
        draft_name = self.get_user_input("草稿名称", default_name)
        if not draft_name:
            return

        # 选择产品型号
        product_model = self.select_product_model()

        # 获取目标时长
        duration_seconds = self.get_user_input(
            f"目标时长(秒)",
            "35",
            int
        )
        if duration_seconds is None:
            return

        target_duration = duration_seconds * 1000000

        # 确认开始
        print(f"\n📋 标准化混剪配置:")
        print(f"  📝 草稿名称: {draft_name}")
        print(f"  📦 产品型号: {product_model or '随机选择'}")
        print(f"  ⏱️  目标时长: {duration_seconds}秒")
        print(f"  🎨 资源库: 完整VIP资源库")
        print(f"  🚫 转场过滤: 排除弹幕类转场")
        print(f"  💯 覆盖率: 100%滤镜、特效、转场覆盖")

        confirm = self.get_user_input("确认开始标准化混剪? (y/n)", "y")
        if confirm is None or confirm.lower() not in ['y', 'yes', '是']:
            print("❌ 用户取消操作")
            return

        try:
            # 创建自动混剪实例
            auto_mix = StandardAutoMix(draft_name)
            auto_mix.set_progress_callback(self.progress_callback)

            print(f"\n🚀 开始执行自动混剪...")

            # 执行混剪
            result = auto_mix.auto_mix(
                target_duration=target_duration,
                product_model=product_model
            )

            print()  # 换行

            if result['success']:
                self.show_standard_success_result(result)
            else:
                print(f"❌ 标准化混剪失败: {result.get('error', 'Unknown error')}")

        except KeyboardInterrupt:
            print("\n\n⏹️  用户中断操作")
        except Exception as e:
            print(f"\n❌ 标准化混剪过程中发生错误: {str(e)}")

    def show_standard_success_result(self, result: Dict[str, Any]):
        """显示标准化混剪成功结果"""
        print("🎉 标准化自动混剪完成！")
        print("-" * 40)
        print(f"📁 草稿路径: {result['draft_path']}")
        print(f"⏱️  视频时长: {result['duration']/1000000:.1f}秒")

        stats = result['statistics']
        print(f"\n📊 标准化混剪统计:")
        print(f"  🎯 产品型号: {stats.get('product_model', 'Unknown')}")
        print(f"  📦 总素材数: {stats['total_materials']}")
        print(f"  ✅ 选择素材: {stats['selected_materials']}个视频")
        print(f"  🎨 应用滤镜: {stats['applied_filters']}个")
        print(f"  ✨ 应用特效: {stats['applied_effects']}个")
        print(f"  🔄 应用转场: {stats['applied_transitions']}个")
        print(f"  🎵 音频轨道: {stats['audio_tracks']}个")
        print(f"  📝 字幕数量: {stats['subtitle_count']}个")

        # 计算覆盖率
        video_count = stats['selected_materials']
        filter_count = stats['applied_filters']
        effect_count = stats['applied_effects']
        transition_count = stats['applied_transitions']

        filter_coverage = (filter_count / video_count * 100) if video_count > 0 else 0
        effect_coverage = (effect_count / video_count * 100) if video_count > 0 else 0
        transition_coverage = (transition_count / (video_count - 1) * 100) if video_count > 1 else 0

        print(f"\n🎉 标准化混剪质量验证:")
        print(f"  📊 滤镜覆盖率: {filter_coverage:.1f}% ({filter_count}/{video_count})")
        print(f"  📊 特效覆盖率: {effect_coverage:.1f}% ({effect_count}/{video_count})")
        print(f"  📊 转场覆盖率: {transition_coverage:.1f}% ({transition_count}/{video_count-1 if video_count > 1 else 0})")

        if filter_coverage >= 100 and effect_coverage >= 100 and transition_coverage >= 100:
            print(f"  ✅ 质量验证: 完美！100%覆盖率达成")
        else:
            print(f"  ⚠️  质量验证: 覆盖率未达到100%")

        print(f"\n🎨 标准化混剪优势:")
        print(f"  🎨 VIP资源: 使用完整的VIP资源库")
        print(f"  🚫 转场过滤: 排除弹幕类转场，专业视觉过渡")
        print(f"  💯 覆盖保证: 确保每个片段都有滤镜和特效")
        print(f"  🔧 兼容稳定: 改进的兼容性和错误处理")
        print(f"  📱 格式优化: 9:16竖屏格式优化")

        print(f"\n💻 剪映验证指南:")
        print(f"  1. 打开剪映，找到草稿 '{result.get('draft_name', 'Unknown')}'")
        print(f"  2. 检查转场效果：应该没有弹幕相关的转场")
        print(f"  3. 验证滤镜特效：每个视频片段都应该有滤镜和特效")
        print(f"  4. 确认音频轨道：应该有解说音频(100%)和背景音效(10%)")
        print(f"  5. 检查字幕：应该有完整的SRT字幕")

    def show_success_result(self, result: Dict[str, Any]):
        """显示成功结果"""
        print("🎉 自动混剪完成！")
        print("-" * 40)
        print(f"📁 草稿路径: {result['draft_path']}")
        print(f"⏱️  视频时长: {result['duration']/1000000:.1f}秒")
        
        stats = result['statistics']
        print(f"\n📊 混剪统计:")
        print(f"  🎯 产品型号: {stats.get('product_model', 'Unknown')}")
        print(f"  📦 总素材数: {stats['total_materials']}")
        print(f"  ✅ 选择素材: {stats['selected_materials']}")
        print(f"  🎨 应用滤镜: {stats['applied_filters']}个")
        print(f"  ✨ 应用特效: {stats['applied_effects']}个")
        print(f"  🔄 应用转场: {stats['applied_transitions']}个")
        print(f"  🎵 音频轨道: {stats['audio_tracks']}个")
        print(f"  📝 字幕数量: {stats['subtitle_count']}个")
        
        print(f"\n💡 使用提示:")
        print(f"  1. 打开剪映专业版")
        print(f"  2. 找到草稿: {os.path.basename(result['draft_path'])}")
        print(f"  3. 检查视频效果并进行微调")
        print(f"  4. 导出最终视频")
        
    def batch_generate(self):
        """批量生成视频"""
        print("\n📊 批量生成视频")
        print("-" * 40)
        print("✨ 功能特色:")
        print("  🎨 完整VIP资源库 (468种滤镜、912种特效、362种转场)")
        print("  🚫 排除弹幕类转场 (专业视觉过渡)")
        print("  💯 100%覆盖率保证 (滤镜、特效、转场)")
        print("  🔧 兼容性改进 (稳定可靠)")
        print("  📱 9:16竖屏优化")
        print("  🚫 支持特效排除管理")
        print("-" * 40)

        # 获取生成数量
        count = self.get_user_input("生成数量", "3", int)
        if count is None or count <= 0:
            return

        # 选择产品型号
        product_model = self.select_product_model()

        # 获取时长范围
        min_seconds = self.get_user_input("最小时长(秒)", "30", int)
        max_seconds = self.get_user_input("最大时长(秒)", "40", int)

        if min_seconds is None or max_seconds is None:
            return

        # 确认批量生成
        print(f"\n📋 批量配置:")
        print(f"  📊 生成数量: {count}个")
        print(f"  📦 产品型号: {product_model or '随机选择'}")
        print(f"  ⏱️  时长范围: {min_seconds}s - {max_seconds}s")
        print(f"  🎨 混剪引擎: 自动混剪 (包含所有优化)")
        print(f"  🚫 转场过滤: 排除弹幕类转场")
        print(f"  💯 覆盖率: 100%滤镜、特效、转场覆盖")
        print(f"  🚫 特效排除: 应用用户自定义排除设置")

        confirm = self.get_user_input("确认开始批量生成? (y/n)", "y")
        if confirm is None or confirm.lower() not in ['y', 'yes', '是']:
            print("❌ 用户取消操作")
            return

        try:
            print(f"\n🚀 开始批量生成 {count} 个视频...")

            # 执行批量生成
            results = self.standard_batch_generate(
                count=count,
                product_model=product_model,
                min_seconds=min_seconds,
                max_seconds=max_seconds
            )

            print()  # 换行

            # 显示批量结果
            self.show_standard_batch_results(results)

        except KeyboardInterrupt:
            print("\n\n⏹️  用户中断批量生成")
        except Exception as e:
            print(f"\n❌ 批量生成过程中发生错误: {str(e)}")

    def standard_batch_generate(self, count: int, product_model: str, min_seconds: int, max_seconds: int):
        """执行批量生成"""
        import random

        results = []

        for i in range(count):
            try:
                # 生成随机时长
                target_seconds = random.randint(min_seconds, max_seconds)
                target_duration = target_seconds * 1000000

                # 生成草稿名称
                timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                draft_name = f"AutoMixBatch_{timestamp}_{i+1:03d}"

                print(f"\n🎬 生成第 {i+1}/{count} 个视频: {draft_name}")
                print(f"  📦 产品型号: {product_model or '随机选择'}")
                print(f"  ⏱️  目标时长: {target_seconds}秒")

                # 创建自动混剪实例
                auto_mix = StandardAutoMix(draft_name)
                auto_mix.set_progress_callback(self.progress_callback)

                # 执行混剪
                result = auto_mix.auto_mix(
                    target_duration=target_duration,
                    product_model=product_model
                )

                if result['success']:
                    results.append({
                        'success': True,
                        'draft_name': draft_name,
                        'draft_path': result['draft_path'],
                        'duration': result['duration'],
                        'statistics': result['statistics']
                    })
                    print(f"  ✅ 成功: {result['duration']/1000000:.1f}秒")
                else:
                    results.append({
                        'success': False,
                        'draft_name': draft_name,
                        'error': result.get('error', 'Unknown error')
                    })
                    print(f"  ❌ 失败: {result.get('error', 'Unknown error')}")

            except Exception as e:
                results.append({
                    'success': False,
                    'draft_name': f"AutoMixBatch_{timestamp}_{i+1:03d}",
                    'error': str(e)
                })
                print(f"  ❌ 异常: {str(e)}")

        return results

    def show_batch_results(self, results: list):
        """显示批量生成结果"""
        success_count = sum(1 for r in results if r['success'])
        
        print(f"🎉 批量生成完成！")
        print(f"✅ 成功: {success_count}/{len(results)}")
        print("-" * 40)
        
        for i, result in enumerate(results, 1):
            if result['success']:
                print(f"{i}. ✅ {result['draft_name']} - {result['duration']/1000000:.1f}s")
            else:
                print(f"{i}. ❌ {result['draft_name']} - {result.get('error', 'Unknown error')}")

    def show_standard_batch_results(self, results: list):
        """显示批量生成结果"""
        success_count = sum(1 for r in results if r['success'])

        print(f"🎉 批量生成完成！")
        print(f"✅ 成功: {success_count}/{len(results)}")
        print("-" * 40)

        # 显示每个结果
        for i, result in enumerate(results, 1):
            if result['success']:
                print(f"{i}. ✅ {result['draft_name']} - {result['duration']/1000000:.1f}s")
            else:
                print(f"{i}. ❌ {result['draft_name']} - {result.get('error', 'Unknown error')}")

        # 显示成功视频的统计信息
        if success_count > 0:
            print(f"\n📊 批量生成统计:")

            # 计算总体统计
            total_filters = 0
            total_effects = 0
            total_transitions = 0
            total_videos = 0
            total_duration = 0

            for result in results:
                if result['success']:
                    stats = result['statistics']
                    total_filters += stats.get('applied_filters', 0)
                    total_effects += stats.get('applied_effects', 0)
                    total_transitions += stats.get('applied_transitions', 0)
                    total_videos += stats.get('selected_materials', 0)
                    total_duration += result['duration']

            avg_filters = total_filters / success_count if success_count > 0 else 0
            avg_effects = total_effects / success_count if success_count > 0 else 0
            avg_transitions = total_transitions / success_count if success_count > 0 else 0
            avg_videos = total_videos / success_count if success_count > 0 else 0
            avg_duration = total_duration / success_count / 1000000 if success_count > 0 else 0

            print(f"  🎯 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
            print(f"  ⏱️  平均时长: {avg_duration:.1f}秒")
            print(f"  📦 平均视频数: {avg_videos:.1f}个/视频")
            print(f"  🎨 平均滤镜数: {avg_filters:.1f}个/视频")
            print(f"  ✨ 平均特效数: {avg_effects:.1f}个/视频")
            print(f"  🔄 平均转场数: {avg_transitions:.1f}个/视频")

            # 计算覆盖率
            filter_coverage = (avg_filters / avg_videos * 100) if avg_videos > 0 else 0
            effect_coverage = (avg_effects / avg_videos * 100) if avg_videos > 0 else 0
            transition_coverage = (avg_transitions / (avg_videos - 1) * 100) if avg_videos > 1 else 0

            print(f"\n🎉 批量质量验证:")
            print(f"  📊 滤镜覆盖率: {filter_coverage:.1f}%")
            print(f"  📊 特效覆盖率: {effect_coverage:.1f}%")
            print(f"  📊 转场覆盖率: {transition_coverage:.1f}%")

            if filter_coverage >= 100 and effect_coverage >= 100 and transition_coverage >= 100:
                print(f"  ✅ 质量验证: 完美！100%覆盖率达成")
            else:
                print(f"  ⚠️  质量验证: 部分覆盖率未达到100%")

            print(f"\n🎨 批量优势:")
            print(f"  🎨 VIP资源: 使用完整的VIP资源库")
            print(f"  🚫 转场过滤: 排除弹幕类转场，专业视觉过渡")
            print(f"  💯 覆盖保证: 确保每个片段都有滤镜和特效")
            print(f"  🔧 兼容稳定: 改进的兼容性和错误处理")
            print(f"  📱 格式优化: 9:16竖屏格式优化")
            print(f"  🚫 特效排除: 应用用户自定义排除设置")
            print(f"  📦 批量高效: 一次生成{success_count}个高质量视频")

            print(f"\n💻 剪映验证指南:")
            print(f"  1. 打开剪映，查看生成的{success_count}个草稿")
            print(f"  2. 检查转场效果：应该没有弹幕相关的转场")
            print(f"  3. 验证滤镜特效：每个视频片段都应该有滤镜和特效")
            print(f"  4. 确认音频轨道：应该有解说音频(100%)和背景音效(10%)")
            print(f"  5. 检查字幕：应该有完整的SRT字幕")

    def effect_exclusion_management(self):
        """特效排除管理"""
        while True:
            print("\n🚫 特效排除管理")
            print("-" * 40)
            stats = self.exclusion_manager.get_exclusion_stats()
            print("📊 当前排除统计:")
            print(f"  🎨 排除滤镜: {stats['filters']}个")
            print(f"  ✨ 排除特效: {stats['effects']}个")
            print(f"  🔄 排除转场: {stats['transitions']}个")
            print("-" * 40)
            print("1. 🎨 管理滤镜排除")
            print("2. ✨ 管理特效排除")
            print("3. 🔄 管理转场排除")
            print("4. 📋 查看排除列表")
            print("5. 🗑️  清空所有排除")
            print("6. 💾 导入/导出排除列表")
            print("0. 🔙 返回主菜单")
            print("-" * 40)

            choice = self.get_user_input("请选择功能", "0", int)
            if choice is None or choice == 0:
                break
            elif choice == 1:
                self.manage_filter_exclusion()
            elif choice == 2:
                self.manage_effect_exclusion()
            elif choice == 3:
                self.manage_transition_exclusion()
            elif choice == 4:
                self.show_exclusion_lists()
            elif choice == 5:
                self.clear_all_exclusions()
            elif choice == 6:
                self.import_export_exclusions()
            else:
                print("❌ 无效选择，请重新输入")

            if choice != 0:
                input("\n按回车键继续...")

    def manage_filter_exclusion(self):
        """管理滤镜排除"""
        while True:
            print("\n🎨 滤镜排除管理")
            print("-" * 40)
            print("1. ➕ 添加排除滤镜")
            print("2. ➖ 移除排除滤镜")
            print("3. 📋 查看可用滤镜")
            print("4. 📋 查看已排除滤镜")
            print("0. 🔙 返回")

            choice = self.get_user_input("请选择操作", "0", int)
            if choice is None or choice == 0:
                break
            elif choice == 1:
                self.add_excluded_filter()
            elif choice == 2:
                self.remove_excluded_filter()
            elif choice == 3:
                self.show_available_filters()
            elif choice == 4:
                self.show_excluded_filters()
            else:
                print("❌ 无效选择")

            if choice != 0:
                input("\n按回车键继续...")

    def manage_effect_exclusion(self):
        """管理特效排除"""
        while True:
            print("\n✨ 特效排除管理")
            print("-" * 40)
            print("1. ➕ 添加排除特效")
            print("2. ➖ 移除排除特效")
            print("3. 📋 查看可用特效")
            print("4. 📋 查看已排除特效")
            print("0. 🔙 返回")

            choice = self.get_user_input("请选择操作", "0", int)
            if choice is None or choice == 0:
                break
            elif choice == 1:
                self.add_excluded_effect()
            elif choice == 2:
                self.remove_excluded_effect()
            elif choice == 3:
                self.show_available_effects()
            elif choice == 4:
                self.show_excluded_effects()
            else:
                print("❌ 无效选择")

            if choice != 0:
                input("\n按回车键继续...")

    def manage_transition_exclusion(self):
        """管理转场排除"""
        while True:
            print("\n🔄 转场排除管理")
            print("-" * 40)
            print("1. ➕ 添加排除转场")
            print("2. ➖ 移除排除转场")
            print("3. 📋 查看可用转场")
            print("4. 📋 查看已排除转场")
            print("0. 🔙 返回")

            choice = self.get_user_input("请选择操作", "0", int)
            if choice is None or choice == 0:
                break
            elif choice == 1:
                self.add_excluded_transition()
            elif choice == 2:
                self.remove_excluded_transition()
            elif choice == 3:
                self.show_available_transitions()
            elif choice == 4:
                self.show_excluded_transitions()
            else:
                print("❌ 无效选择")

            if choice != 0:
                input("\n按回车键继续...")

    def add_excluded_filter(self):
        """添加排除滤镜"""
        print("\n➕ 添加排除滤镜")
        print("-" * 40)

        # 获取可用滤镜
        available_filters = self.exclusion_manager.get_filtered_filters()
        all_filters = self.exclusion_manager.metadata_manager.get_available_filters()
        excludable_filters = [f for f in all_filters if f.name not in self.exclusion_manager.excluded_filters]

        if not excludable_filters:
            print("❌ 没有可排除的滤镜")
            return

        print("📋 可用滤镜列表 (输入序号选择):")
        for i, filter_meta in enumerate(excludable_filters[:20], 1):
            print(f"  {i}. {filter_meta.name}")

        if len(excludable_filters) > 20:
            print(f"  ... 还有{len(excludable_filters) - 20}个滤镜")
            print("💡 提示: 也可以直接输入滤镜名称")

        choice = self.get_user_input("请输入序号或滤镜名称")
        if not choice:
            return

        # 尝试按序号选择
        try:
            index = int(choice) - 1
            if 0 <= index < min(20, len(excludable_filters)):
                selected_filter = excludable_filters[index]
                if self.exclusion_manager.add_excluded_filter(selected_filter.name):
                    print(f"✅ 已添加排除滤镜: {selected_filter.name}")
                else:
                    print(f"⚠️  滤镜已在排除列表中: {selected_filter.name}")
                return
        except ValueError:
            pass

        # 尝试按名称选择
        for filter_meta in excludable_filters:
            if choice.lower() in filter_meta.name.lower():
                if self.exclusion_manager.add_excluded_filter(filter_meta.name):
                    print(f"✅ 已添加排除滤镜: {filter_meta.name}")
                else:
                    print(f"⚠️  滤镜已在排除列表中: {filter_meta.name}")
                return

        print("❌ 未找到匹配的滤镜")

    def remove_excluded_filter(self):
        """移除排除滤镜"""
        print("\n➖ 移除排除滤镜")
        print("-" * 40)

        if not self.exclusion_manager.excluded_filters:
            print("❌ 没有已排除的滤镜")
            return

        excluded_list = list(self.exclusion_manager.excluded_filters)
        print("📋 已排除滤镜列表:")
        for i, filter_name in enumerate(excluded_list, 1):
            print(f"  {i}. {filter_name}")

        choice = self.get_user_input("请输入序号")
        if not choice:
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(excluded_list):
                removed_filter = excluded_list[index]
                if self.exclusion_manager.remove_excluded_filter(removed_filter):
                    print(f"✅ 已移除排除滤镜: {removed_filter}")
                else:
                    print(f"⚠️  移除失败: {removed_filter}")
            else:
                print("❌ 无效序号")
        except ValueError:
            print("❌ 请输入有效数字")

    def add_excluded_effect(self):
        """添加排除特效（简化版本）"""
        print("\n➕ 添加排除特效")
        print("-" * 40)
        effect_name = self.get_user_input("请输入特效名称")
        if effect_name and self.exclusion_manager.add_excluded_effect(effect_name):
            print(f"✅ 已添加排除特效: {effect_name}")
        else:
            print("❌ 添加失败或特效已存在")

    def remove_excluded_effect(self):
        """移除排除特效（简化版本）"""
        print("\n➖ 移除排除特效")
        print("-" * 40)
        if not self.exclusion_manager.excluded_effects:
            print("❌ 没有已排除的特效")
            return

        excluded_list = list(self.exclusion_manager.excluded_effects)
        for i, effect_name in enumerate(excluded_list, 1):
            print(f"  {i}. {effect_name}")

        choice = self.get_user_input("请输入序号")
        if choice:
            try:
                index = int(choice) - 1
                if 0 <= index < len(excluded_list):
                    removed_effect = excluded_list[index]
                    if self.exclusion_manager.remove_excluded_effect(removed_effect):
                        print(f"✅ 已移除排除特效: {removed_effect}")
            except ValueError:
                print("❌ 请输入有效数字")

    def add_excluded_transition(self):
        """添加排除转场（简化版本）"""
        print("\n➕ 添加排除转场")
        print("-" * 40)
        transition_name = self.get_user_input("请输入转场名称")
        if transition_name and self.exclusion_manager.add_excluded_transition(transition_name):
            print(f"✅ 已添加排除转场: {transition_name}")
        else:
            print("❌ 添加失败或转场已存在")

    def remove_excluded_transition(self):
        """移除排除转场（简化版本）"""
        print("\n➖ 移除排除转场")
        print("-" * 40)
        if not self.exclusion_manager.excluded_transitions:
            print("❌ 没有已排除的转场")
            return

        excluded_list = list(self.exclusion_manager.excluded_transitions)
        for i, transition_name in enumerate(excluded_list, 1):
            print(f"  {i}. {transition_name}")

        choice = self.get_user_input("请输入序号")
        if choice:
            try:
                index = int(choice) - 1
                if 0 <= index < len(excluded_list):
                    removed_transition = excluded_list[index]
                    if self.exclusion_manager.remove_excluded_transition(removed_transition):
                        print(f"✅ 已移除排除转场: {removed_transition}")
            except ValueError:
                print("❌ 请输入有效数字")

    def show_exclusion_lists(self):
        """显示所有排除列表"""
        print("\n📋 排除列表总览")
        print("-" * 40)

        print("🎨 排除滤镜:")
        if self.exclusion_manager.excluded_filters:
            for i, name in enumerate(list(self.exclusion_manager.excluded_filters)[:10], 1):
                print(f"  {i}. {name}")
            if len(self.exclusion_manager.excluded_filters) > 10:
                print(f"  ... 还有{len(self.exclusion_manager.excluded_filters) - 10}个")
        else:
            print("  无")

        print("\n✨ 排除特效:")
        if self.exclusion_manager.excluded_effects:
            for i, name in enumerate(list(self.exclusion_manager.excluded_effects)[:10], 1):
                print(f"  {i}. {name}")
            if len(self.exclusion_manager.excluded_effects) > 10:
                print(f"  ... 还有{len(self.exclusion_manager.excluded_effects) - 10}个")
        else:
            print("  无")

        print("\n🔄 排除转场:")
        if self.exclusion_manager.excluded_transitions:
            for i, name in enumerate(list(self.exclusion_manager.excluded_transitions)[:10], 1):
                print(f"  {i}. {name}")
            if len(self.exclusion_manager.excluded_transitions) > 10:
                print(f"  ... 还有{len(self.exclusion_manager.excluded_transitions) - 10}个")
        else:
            print("  无")

    def clear_all_exclusions(self):
        """清空所有排除列表"""
        print("\n🗑️  清空所有排除列表")
        print("-" * 40)
        confirm = self.get_user_input("确认清空所有排除列表? (y/n)", "n")
        if confirm and confirm.lower() in ['y', 'yes', '是']:
            self.exclusion_manager.clear_all_exclusions()
            print("✅ 已清空所有排除列表")
        else:
            print("❌ 操作已取消")

    # 添加占位方法
    def show_available_filters(self):
        print("📋 可用滤镜功能开发中...")

    def show_excluded_filters(self):
        print("📋 已排除滤镜功能开发中...")

    def show_available_effects(self):
        print("📋 可用特效功能开发中...")

    def show_excluded_effects(self):
        print("📋 已排除特效功能开发中...")

    def show_available_transitions(self):
        print("📋 可用转场功能开发中...")

    def show_excluded_transitions(self):
        print("📋 已排除转场功能开发中...")

    def import_export_exclusions(self):
        print("💾 导入/导出功能开发中...")

    def pexels_overlay_management(self):
        """Pexels防审核覆盖层管理"""
        while True:
            print("\n🛡️  Pexels防审核覆盖层设置")
            print("-" * 40)
            print("💡 功能说明:")
            print("  • 在素材视频之上添加一层热门视频")
            print("  • 15%不透明度，防止平台抽帧审核")
            print("  • 滤镜、特效、字幕放在覆盖层之上")
            print("-" * 40)

            # 显示当前配置
            api_key = self.config_manager.get_pexels_api_key()
            is_enabled = self.config_manager.is_pexels_overlay_enabled()
            opacity = self.config_manager.get_pexels_overlay_opacity()

            print("📊 当前配置:")
            print(f"  🔑 API密钥: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else api_key}")
            print(f"  🛡️  防审核层: {'启用' if is_enabled else '禁用'}")
            print(f"  🌫️  不透明度: {opacity:.1%}")

            print("-" * 40)
            print("1. 🔑 设置API密钥")
            print("2. 🛡️  启用/禁用防审核层")
            print("3. 🌫️  设置不透明度")
            print("4. 🧪 测试API密钥")
            print("5. 📁 查看缓存信息")
            print("6. 🗑️  清理缓存")
            print("0. 🔙 返回主菜单")
            print("-" * 40)

            choice = self.get_user_input("请选择功能", "0", int)
            if choice is None or choice == 0:
                break
            elif choice == 1:
                self.set_pexels_api_key()
            elif choice == 2:
                self.toggle_pexels_overlay()
            elif choice == 3:
                self.set_pexels_opacity()
            elif choice == 4:
                self.test_pexels_api()
            elif choice == 5:
                self.show_pexels_cache_info()
            elif choice == 6:
                self.clear_pexels_cache()
            else:
                print("❌ 无效选择，请重新输入")

            if choice != 0:
                input("\n按回车键继续...")

    def set_pexels_api_key(self):
        """设置Pexels API密钥"""
        print("\n🔑 设置Pexels API密钥")
        print("-" * 40)
        print("💡 获取API密钥:")
        print("  1. 访问 https://www.pexels.com/api/")
        print("  2. 注册账户并申请API密钥")
        print("  3. 将密钥粘贴到下方")
        print("-" * 40)

        current_key = self.config_manager.get_pexels_api_key()
        new_key = self.get_user_input(
            f"请输入新的API密钥 (当前: {current_key[:20]}...)",
            current_key
        )

        if new_key and new_key != current_key:
            if self.config_manager.set_pexels_api_key(new_key):
                print(f"✅ API密钥已更新")

                # 测试新密钥
                print("🧪 测试新密钥...")
                from JianYingDraft.core.pexelsManager import PexelsManager
                pexels = PexelsManager(new_key)
                if pexels.test_api_key():
                    print("✅ 新API密钥验证成功")
                else:
                    print("❌ 新API密钥验证失败，请检查密钥是否正确")
            else:
                print("❌ API密钥更新失败")
        else:
            print("❌ 未更新API密钥")

    def toggle_pexels_overlay(self):
        """切换Pexels防审核覆盖层启用状态"""
        current_state = self.config_manager.is_pexels_overlay_enabled()
        new_state = not current_state

        if self.config_manager.set_pexels_overlay_enabled(new_state):
            status = "启用" if new_state else "禁用"
            print(f"✅ Pexels防审核覆盖层已{status}")
        else:
            print("❌ 设置失败")

    def set_pexels_opacity(self):
        """设置Pexels防审核覆盖层不透明度"""
        print("\n🌫️  设置防审核覆盖层不透明度")
        print("-" * 40)

        current_opacity = self.config_manager.get_pexels_overlay_opacity()
        print(f"当前不透明度: {current_opacity:.1%}")
        print("建议范围: 3% - 10% (防审核效果最佳)")
        print("💡 5%是推荐值，既能防审核又几乎不影响观看")

        new_opacity = self.get_user_input(
            "请输入新的不透明度 (0.03-0.1)",
            str(current_opacity),
            float
        )

        if new_opacity is not None:
            if 0.03 <= new_opacity <= 0.1:
                if self.config_manager.set_pexels_overlay_opacity(new_opacity):
                    print(f"✅ 不透明度已设置为 {new_opacity:.1%}")
                else:
                    print("❌ 设置失败")
            else:
                print("❌ 不透明度必须在 0.03 - 0.1 之间")
        else:
            print("❌ 输入无效")

    def test_pexels_api(self):
        """测试Pexels API密钥"""
        print("\n🧪 测试Pexels API密钥")
        print("-" * 40)

        try:
            from JianYingDraft.core.pexelsManager import PexelsManager
            pexels = PexelsManager()

            if pexels.test_api_key():
                print("✅ API密钥验证成功")

                # 尝试获取一个热门视频
                print("🎬 测试获取热门视频...")
                video_data = pexels.get_popular_videos(per_page=1)
                if video_data and video_data.get('videos'):
                    video = video_data['videos'][0]
                    print(f"✅ 成功获取视频: ID {video['id']}, 时长 {video.get('duration', 0)}秒")
                else:
                    print("⚠️  API密钥有效，但获取视频失败")
            else:
                print("❌ API密钥验证失败")

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")

    def show_pexels_cache_info(self):
        """显示Pexels缓存信息"""
        print("\n📁 Pexels缓存信息")
        print("-" * 40)

        try:
            from JianYingDraft.core.pexelsManager import PexelsManager
            pexels = PexelsManager()
            cache_info = pexels.get_cache_info()

            print(f"📁 缓存文件数: {cache_info['file_count']}个")
            print(f"💾 总大小: {cache_info.get('total_size_mb', 0):.1f}MB")
            print(f"📂 缓存目录: {pexels.cache_dir}")

        except Exception as e:
            print(f"❌ 获取缓存信息失败: {str(e)}")

    def clear_pexels_cache(self):
        """清理Pexels缓存"""
        print("\n🗑️  清理Pexels缓存")
        print("-" * 40)

        confirm = self.get_user_input("确认清理所有缓存文件? (y/n)", "n")
        if confirm and confirm.lower() in ['y', 'yes', '是']:
            try:
                from JianYingDraft.core.pexelsManager import PexelsManager
                pexels = PexelsManager()
                pexels.clear_cache()
                print("✅ 缓存已清理")
            except Exception as e:
                print(f"❌ 清理失败: {str(e)}")
        else:
            print("❌ 操作已取消")

    def show_help(self):
        """显示帮助信息"""
        print("\n❓ 帮助信息")
        print("-" * 40)
        print("🎯 功能说明:")
        print("  • 自动混剪: 从素材库智能选择视频片段进行混剪")
        print("  • 批量生成: 一次性生成多个不同的混剪视频")
        print("  • 智能特效: 自动添加滤镜、特效、转场效果")
        print("  • 字幕支持: 自动添加SRT字幕文件")
        print("  • 音频处理: 支持解说音频和背景音乐")
        print()
        print("📁 素材库结构:")
        print("  素材库/")
        print("  ├── A83/          # 产品型号文件夹")
        print("  │   ├── 使用场景/  # 子场景文件夹")
        print("  │   ├── 摆拍/")
        print("  │   └── ...")
        print("  └── 音效/          # 背景音效文件夹")
        print()
        print("🎬 输出格式:")
        print("  • 视频比例: 9:16 (竖屏)")
        print("  • 视频静音: 自动静音原声")
        print("  • 音频轨道: 解说音频 + 背景音乐")
        print("  • 特效分布: 每个片段随机特效")
        
    def run(self):
        """运行交互式工具"""
        self.show_banner()
        
        while True:
            try:
                self.show_main_menu()
                choice = self.get_user_input("请选择功能", "1", int)
                
                if choice is None:
                    continue
                elif choice == 0:
                    print("\n👋 感谢使用剪映自动混剪工具！")
                    break
                elif choice == 1:
                    self.start_standard_auto_mix()
                elif choice == 2:
                    self.batch_generate()
                elif choice == 3:
                    self.effect_exclusion_management()
                elif choice == 4:
                    self.pexels_overlay_management()
                elif choice == 5:
                    self.show_config_info()
                elif choice == 6:
                    self.modify_config()
                elif choice == 7:
                    self.show_help()
                else:
                    print("❌ 无效选择，请重新输入")
                    
                # 等待用户按键继续
                if choice != 0:
                    input("\n按回车键继续...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用剪映自动混剪工具！")
                break
            except Exception as e:
                print(f"\n❌ 程序错误: {str(e)}")
                input("按回车键继续...")


if __name__ == "__main__":
    app = InteractiveAutoMix()
    app.run()
