#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Web界面自动补全功能
"""

import requests
import json

def test_autocomplete_functionality():
    """测试自动补全功能"""
    base_url = "http://localhost:5000"
    
    print("🔍 测试Web界面自动补全功能")
    print("=" * 50)
    
    # 测试获取可用特效列表
    print("\n📋 测试获取可用特效列表...")
    try:
        response = requests.get(f"{base_url}/api/effects/available")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                effects_data = data['data']
                print(f"✅ 成功获取特效列表:")
                print(f"  🎨 可用滤镜: {len(effects_data.get('filters', []))}个")
                print(f"  ✨ 可用特效: {len(effects_data.get('effects', []))}个")
                print(f"  🔄 可用转场: {len(effects_data.get('transitions', []))}个")
                
                # 测试搜索功能
                print("\n🔍 测试搜索功能:")
                
                # 搜索包含"光"的特效
                light_effects = [e for e in effects_data.get('effects', []) if '光' in e]
                print(f"  包含'光'的特效: {len(light_effects)}个")
                if light_effects:
                    print(f"    示例: {light_effects[:5]}")
                
                # 搜索包含"模糊"的滤镜
                blur_filters = [f for f in effects_data.get('filters', []) if '模糊' in f]
                print(f"  包含'模糊'的滤镜: {len(blur_filters)}个")
                if blur_filters:
                    print(f"    示例: {blur_filters[:5]}")
                
                # 搜索包含"淡"的转场
                fade_transitions = [t for t in effects_data.get('transitions', []) if '淡' in t]
                print(f"  包含'淡'的转场: {len(fade_transitions)}个")
                if fade_transitions:
                    print(f"    示例: {fade_transitions[:5]}")
                
                return effects_data
            else:
                print(f"❌ 获取失败: {data.get('error', '未知错误')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_search_patterns(effects_data):
    """测试各种搜索模式"""
    if not effects_data:
        return
    
    print("\n🔍 测试搜索模式:")
    
    # 测试不同的搜索关键词
    search_terms = [
        ('爱心', 'effects'),
        ('故障', 'effects'),
        ('复古', 'filters'),
        ('模糊', 'filters'),
        ('推拉', 'transitions'),
        ('旋转', 'transitions')
    ]
    
    for term, effect_type in search_terms:
        effect_list = effects_data.get(effect_type, [])
        matches = [item for item in effect_list if term in item]
        type_label = {'effects': '特效', 'filters': '滤镜', 'transitions': '转场'}[effect_type]
        
        print(f"  搜索'{term}' ({type_label}): {len(matches)}个匹配")
        if matches:
            print(f"    示例: {matches[:3]}")

def test_add_exclusion_with_search(effects_data):
    """测试通过搜索添加排除项"""
    if not effects_data:
        return
    
    print("\n➕ 测试通过搜索添加排除项...")
    
    # 选择一个包含"光"的特效进行测试
    light_effects = [e for e in effects_data.get('effects', []) if '光' in e]
    if light_effects:
        test_effect = light_effects[0]
        print(f"  测试添加特效: {test_effect}")
        
        try:
            response = requests.post(
                "http://localhost:5000/api/exclusions/effects/add",
                json={"name": test_effect},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"  ✅ 成功添加排除项: {test_effect}")
                    
                    # 验证是否添加成功
                    response = requests.get("http://localhost:5000/api/exclusions")
                    if response.status_code == 200:
                        exclusions = response.json()
                        if test_effect in exclusions['effects']['excluded_list']:
                            print(f"  ✅ 验证成功: {test_effect} 已在排除列表中")
                            
                            # 移除测试项
                            response = requests.post(
                                "http://localhost:5000/api/exclusions/effects/remove",
                                json={"name": test_effect},
                                headers={"Content-Type": "application/json"}
                            )
                            if response.status_code == 200 and response.json()['success']:
                                print(f"  🧹 已清理测试项: {test_effect}")
                        else:
                            print(f"  ❌ 验证失败: {test_effect} 不在排除列表中")
                else:
                    print(f"  ❌ 添加失败: {data.get('error', '未知错误')}")
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")

def main():
    """主函数"""
    effects_data = test_autocomplete_functionality()
    test_search_patterns(effects_data)
    test_add_exclusion_with_search(effects_data)
    
    print("\n🎉 自动补全功能测试完成!")
    print("\n💡 使用说明:")
    print("  1. 在Web界面的输入框中输入关键词")
    print("  2. 系统会自动显示匹配的特效列表")
    print("  3. 点击或使用键盘选择要添加的特效")
    print("  4. 点击'添加排除'按钮完成操作")

if __name__ == "__main__":
    main()
