#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试智能排除夸张特效功能
"""

from JianYingDraft.core.effectExclusionManager import EffectExclusionManager
from JianYingDraft.core.metadataManager import MetadataManager

def test_smart_exclude():
    """测试智能排除功能"""
    print("🚀 开始测试智能排除夸张特效功能...")
    
    # 初始化管理器
    metadata_manager = MetadataManager()
    exclusion_manager = EffectExclusionManager(metadata_manager)
    
    # 获取预览
    print("\n📋 获取夸张特效预览...")
    preview = exclusion_manager.get_exaggerated_effects_preview()
    
    print(f"✨ 将被排除的特效: {len(preview['effects'])}个")
    print(f"🎨 将被排除的滤镜: {len(preview['filters'])}个")
    
    if preview['effects']:
        print("\n🔍 夸张特效示例:")
        for i, effect_name in enumerate(preview['effects'][:15], 1):
            print(f"  {i:2d}. {effect_name}")
        if len(preview['effects']) > 15:
            print(f"  ... 还有{len(preview['effects']) - 15}个特效")
    
    if preview['filters']:
        print("\n🎨 夸张滤镜示例:")
        for i, filter_name in enumerate(preview['filters'][:10], 1):
            print(f"  {i:2d}. {filter_name}")
        if len(preview['filters']) > 10:
            print(f"  ... 还有{len(preview['filters']) - 10}个滤镜")
    
    # 询问是否执行排除
    print("\n⚠️  注意: 此操作将排除这些特效，使视频更加专业")
    confirm = input("确认执行智能排除? (y/n): ").strip().lower()
    
    if confirm == 'y':
        print("\n🚀 开始智能排除...")
        excluded_count = exclusion_manager.auto_exclude_exaggerated_effects()
        
        print("✅ 智能排除完成!")
        print(f"  ✨ 排除特效: {excluded_count['effects']}个")
        print(f"  🎨 排除滤镜: {excluded_count['filters']}个")
        print("💡 现在视频特效将更加专业和适合商业使用")
        
        # 显示排除后的统计
        print("\n📊 排除后统计:")
        all_effects = metadata_manager.get_available_effects()
        all_filters = metadata_manager.get_available_filters()
        
        available_effects = [e for e in all_effects if e.name not in exclusion_manager.excluded_effects]
        available_filters = [f for f in all_filters if f.name not in exclusion_manager.excluded_filters]
        
        print(f"  ✨ 可用特效: {len(available_effects)}个 (总共{len(all_effects)}个)")
        print(f"  🎨 可用滤镜: {len(available_filters)}个 (总共{len(all_filters)}个)")
        
    else:
        print("❌ 操作已取消")

if __name__ == "__main__":
    test_smart_exclude()
