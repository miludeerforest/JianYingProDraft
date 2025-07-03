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
        print("-" * 40)
        
        try:
            print(f"📁 素材库路径: {self.config_manager.get_material_path()}")
            print(f"💾 草稿输出路径: {self.config_manager.get_draft_output_path()}")
            
            min_dur, max_dur = self.config_manager.get_video_duration_range()
            print(f"⏱️  视频时长范围: {min_dur//1000000}s - {max_dur//1000000}s")
            
            print(f"✨ 特效概率: {self.config_manager.get_effect_probability():.0%}")
            print(f"🎨 滤镜概率: {self.config_manager.get_filter_probability():.0%}")
            print(f"🔄 转场概率: {self.config_manager.get_transition_probability():.0%}")
            
            narration_vol, background_vol = self.config_manager.get_audio_volumes()
            print(f"🎵 音频音量: 解说{narration_vol:.0%}, 背景{background_vol:.0%}")
            
            print(f"🔇 视频去前: {self.config_manager.get_trim_start_duration()//1000000}秒")
            print(f"🔍 画面缩放: {self.config_manager.get_video_scale_factor():.0%}")
            
        except Exception as e:
            print(f"❌ 读取配置失败: {str(e)}")
            
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
                    print("\n🔧 配置修改功能开发中...")
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
