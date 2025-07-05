#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Web API功能
"""

import requests
import json

def test_web_api():
    """测试Web API功能"""
    base_url = "http://localhost:5000"
    
    print("🌐 测试Web API功能")
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
                
                # 显示一些示例
                if effects_data.get('effects'):
                    print(f"\n  特效示例:")
                    for i, effect in enumerate(effects_data['effects'][:5], 1):
                        print(f"    {i}. {effect}")
            else:
                print(f"❌ 获取失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试获取排除列表
    print("\n📋 测试获取排除列表...")
    try:
        response = requests.get(f"{base_url}/api/exclusions")
        if response.status_code == 200:
            data = response.json()
            if not data.get('error'):
                print(f"✅ 成功获取排除列表:")
                print(f"  🎨 已排除滤镜: {data['filters']['excluded']}个")
                print(f"  ✨ 已排除特效: {data['effects']['excluded']}个")
                print(f"  🔄 已排除转场: {data['transitions']['excluded']}个")
            else:
                print(f"❌ 获取失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试添加排除项（使用一个测试特效）
    print("\n➕ 测试添加排除项...")
    test_effect_name = "测试特效"  # 这个特效可能不存在，但可以测试API
    try:
        response = requests.post(
            f"{base_url}/api/exclusions/effects/add",
            json={"name": test_effect_name},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ 成功添加排除项: {test_effect_name}")
            else:
                print(f"⚠️  添加失败（预期）: {data.get('error', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 测试智能排除功能
    print("\n🚫 测试智能排除功能...")
    try:
        response = requests.post(
            f"{base_url}/api/exclusions/smart-exclude",
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                excluded_count = data['excluded_count']
                print(f"✅ 智能排除成功:")
                print(f"  ✨ 排除特效: {excluded_count['effects']}个")
                print(f"  🎨 排除滤镜: {excluded_count['filters']}个")
            else:
                print(f"❌ 智能排除失败: {data.get('error', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n🎉 Web API测试完成!")

if __name__ == "__main__":
    test_web_api()
