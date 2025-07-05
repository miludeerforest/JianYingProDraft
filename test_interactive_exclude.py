#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试交互式特效排除管理功能
"""

from JianYingDraft.core.effectExclusionManager import EffectExclusionManager
from JianYingDraft.core.metadataManager import MetadataManager

def test_interactive_exclude():
    """测试交互式特效排除管理"""
    print("🚫 特效排除管理测试")
    print("-" * 60)
    
    # 初始化管理器
    metadata_manager = MetadataManager()
    exclusion_manager = EffectExclusionManager(metadata_manager)
    
    while True:
        print("\n📋 特效排除管理菜单:")
        print("1. 🎨 管理滤镜排除")
        print("2. ✨ 管理特效排除")
        print("3. 🔄 管理转场排除")
        print("4. 📋 查看排除列表")
        print("5. 🚫 智能排除夸张特效")
        print("6. 🗑️  清空所有排除")
        print("7. 💾 导入/导出排除列表")
        print("0. 🔙 退出")
        
        choice = input("\n请选择功能 (默认: 0): ").strip()
        if not choice:
            choice = "0"
        
        try:
            choice = int(choice)
        except ValueError:
            print("❌ 无效选择，请输入数字")
            continue
        
        if choice == 0:
            print("👋 退出特效排除管理")
            break
        elif choice == 4:
            show_exclusion_lists(exclusion_manager)
        elif choice == 5:
            smart_exclude_exaggerated_effects(exclusion_manager)
        else:
            print(f"❌ 功能 {choice} 暂未实现")

def show_exclusion_lists(exclusion_manager):
    """显示排除列表"""
    print("\n📋 当前排除列表")
    print("-" * 40)
    
    print(f"✨ 已排除特效: {len(exclusion_manager.excluded_effects)}个")
    if exclusion_manager.excluded_effects:
        print("  示例:")
        for i, effect_name in enumerate(sorted(exclusion_manager.excluded_effects)[:10], 1):
            print(f"  {i:2d}. {effect_name}")
        if len(exclusion_manager.excluded_effects) > 10:
            print(f"  ... 还有{len(exclusion_manager.excluded_effects) - 10}个特效")
    
    print(f"\n🎨 已排除滤镜: {len(exclusion_manager.excluded_filters)}个")
    if exclusion_manager.excluded_filters:
        print("  示例:")
        for i, filter_name in enumerate(sorted(exclusion_manager.excluded_filters), 1):
            print(f"  {i:2d}. {filter_name}")
    
    print(f"\n🔄 已排除转场: {len(exclusion_manager.excluded_transitions)}个")
    if exclusion_manager.excluded_transitions:
        print("  示例:")
        for i, transition_name in enumerate(sorted(exclusion_manager.excluded_transitions), 1):
            print(f"  {i:2d}. {transition_name}")

def smart_exclude_exaggerated_effects(exclusion_manager):
    """智能排除夸张特效"""
    print("\n🚫 智能排除夸张特效")
    print("-" * 60)
    print("💡 功能说明:")
    print("  • 自动识别并排除过于夸张、不适合商业视频的特效")
    print("  • 包括恐怖、卡通、故障、过时等类型的特效")
    print("  • 保留专业、简洁、适合商业使用的特效")
    print("-" * 60)
    
    # 获取预览
    try:
        preview = exclusion_manager.get_exaggerated_effects_preview()
        
        print("📋 将被排除的夸张特效预览:")
        print(f"  ✨ 特效: {len(preview['effects'])}个")
        print(f"  🎨 滤镜: {len(preview['filters'])}个")
        
        if preview['effects'] or preview['filters']:
            print("\n🔍 部分示例:")
            
            # 显示特效示例
            if preview['effects']:
                print("  ✨ 特效示例:")
                for i, effect_name in enumerate(preview['effects'][:10], 1):
                    print(f"    {i:2d}. {effect_name}")
                if len(preview['effects']) > 10:
                    print(f"    ... 还有{len(preview['effects']) - 10}个特效")
            
            # 显示滤镜示例
            if preview['filters']:
                print("  🎨 滤镜示例:")
                for i, filter_name in enumerate(preview['filters'][:5], 1):
                    print(f"    {i:2d}. {filter_name}")
                if len(preview['filters']) > 5:
                    print(f"    ... 还有{len(preview['filters']) - 5}个滤镜")
            
            print("\n⚠️  注意: 此操作将排除这些特效，使视频更加专业")
            confirm = input("确认执行智能排除? (y/n): ").strip().lower()
            
            if confirm == 'y':
                print("\n🚀 开始智能排除...")
                excluded_count = exclusion_manager.auto_exclude_exaggerated_effects()
                
                print("✅ 智能排除完成!")
                print(f"  ✨ 排除特效: {excluded_count['effects']}个")
                print(f"  🎨 排除滤镜: {excluded_count['filters']}个")
                print("💡 现在视频特效将更加专业和适合商业使用")
            else:
                print("❌ 操作已取消")
        else:
            print("✅ 没有发现需要排除的夸张特效")
            print("💡 当前特效库已经比较专业")
            
    except Exception as e:
        print(f"❌ 智能排除失败: {str(e)}")

if __name__ == "__main__":
    test_interactive_exclude()
