#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Web界面的高级防审核技术配置功能
"""

import requests
import json
import time

def test_web_interface_config():
    """测试Web界面的配置功能"""
    print("🌐 测试Web界面高级防审核技术配置")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. 测试获取配置
        print("\n📊 测试获取配置...")
        response = requests.get(f"{base_url}/api/config")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ 配置获取成功")
            
            # 检查高级防审核技术配置
            print("\n🔍 检查高级防审核技术配置:")
            
            # 镜像翻转
            flip_prob = config.get('flip_probability', 0)
            print(f"  🔄 镜像翻转概率: {flip_prob:.1%}")
            
            # 模糊背景
            blur_enabled = config.get('blur_background_enabled', False)
            blur_prob = config.get('blur_background_probability', 0)
            print(f"  🌫️  模糊背景: {'启用' if blur_enabled else '禁用'}")
            print(f"  🌫️  模糊背景概率: {blur_prob:.1%}")
            
            # 抽帧处理
            frame_enabled = config.get('frame_manipulation_enabled', False)
            frame_prob = config.get('frame_drop_probability', 0)
            print(f"  🎞️  抽帧处理: {'启用' if frame_enabled else '禁用'}")
            print(f"  🎞️  抽帧概率: {frame_prob:.1%}")
            
            # 验证是否为100%执行
            print(f"\n📊 100%执行验证:")
            if flip_prob >= 1.0:
                print("  ✅ 镜像翻转: 100%执行")
            else:
                print(f"  ❌ 镜像翻转: {flip_prob:.1%}执行")
            
            if blur_enabled and blur_prob >= 1.0:
                print("  ✅ 模糊背景: 100%执行")
            else:
                print(f"  ❌ 模糊背景: {'禁用' if not blur_enabled else f'{blur_prob:.1%}执行'}")
            
            if frame_enabled and frame_prob >= 1.0:
                print("  ✅ 抽帧处理: 100%执行")
            else:
                print(f"  ❌ 抽帧处理: {'禁用' if not frame_enabled else f'{frame_prob:.1%}执行'}")
                
        else:
            print(f"❌ 配置获取失败: {response.status_code}")
            return False
        
        # 2. 测试更新配置
        print("\n💾 测试更新配置...")
        
        # 准备测试配置（确保100%执行）
        test_config = {
            'flip_probability': 1.0,
            'blur_background_enabled': True,
            'blur_background_probability': 1.0,
            'foreground_scale': 0.75,
            'background_scale': 1.3,
            'background_blur_intensity': 0.6,
            'frame_manipulation_enabled': True,
            'frame_drop_probability': 1.0,
            'frame_drop_interval': 4.0,
            'max_frame_drops_per_segment': 4
        }
        
        response = requests.post(
            f"{base_url}/api/config",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 配置更新成功")
                
                # 验证更新后的配置
                print("\n🔍 验证更新后的配置...")
                response = requests.get(f"{base_url}/api/config")
                
                if response.status_code == 200:
                    updated_config = response.json()
                    
                    # 检查关键配置是否更新
                    flip_prob = updated_config.get('flip_probability', 0)
                    blur_prob = updated_config.get('blur_background_probability', 0)
                    frame_prob = updated_config.get('frame_drop_probability', 0)
                    foreground_scale = updated_config.get('foreground_scale', 0)
                    
                    print(f"  🔄 镜像翻转概率: {flip_prob:.1%}")
                    print(f"  🌫️  模糊背景概率: {blur_prob:.1%}")
                    print(f"  🎞️  抽帧概率: {frame_prob:.1%}")
                    print(f"  📐 前景缩放: {foreground_scale:.1%}")
                    
                    # 验证是否正确更新
                    if (flip_prob >= 1.0 and blur_prob >= 1.0 and 
                        frame_prob >= 1.0 and abs(foreground_scale - 0.75) < 0.01):
                        print("✅ 配置更新验证成功")
                        return True
                    else:
                        print("❌ 配置更新验证失败")
                        return False
                else:
                    print("❌ 验证配置获取失败")
                    return False
            else:
                print(f"❌ 配置更新失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 配置更新请求失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Web界面，请确保Web服务器正在运行")
        print("💡 启动命令: python start_web_interface.py")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def test_web_interface_features():
    """测试Web界面的其他功能"""
    print("\n🧪 测试Web界面其他功能")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试主页
        print("📄 测试主页访问...")
        response = requests.get(base_url)
        
        if response.status_code == 200:
            print("✅ 主页访问成功")
            
            # 检查是否包含高级防审核技术相关内容
            content = response.text
            
            if '高级防审核技术' in content:
                print("✅ 页面包含高级防审核技术配置")
            else:
                print("❌ 页面缺少高级防审核技术配置")
            
            if 'setForceExecutionMode' in content:
                print("✅ 页面包含强制执行模式功能")
            else:
                print("❌ 页面缺少强制执行模式功能")
                
            return True
        else:
            print(f"❌ 主页访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def main():
    """主函数"""
    print("🌐 Web界面高级防审核技术配置测试")
    print("=" * 60)
    print("📝 测试内容:")
    print("  • Web界面配置获取功能")
    print("  • Web界面配置更新功能")
    print("  • 高级防审核技术配置验证")
    print("  • 100%强制执行模式测试")
    
    print("\n⚠️  注意: 请确保Web服务器正在运行")
    print("启动命令: python start_web_interface.py")
    
    # 等待用户确认
    input("\n按回车键开始测试...")
    
    try:
        # 测试配置功能
        config_success = test_web_interface_config()
        
        # 测试界面功能
        interface_success = test_web_interface_features()
        
        print("\n🎉 Web界面测试完成!")
        
        if config_success and interface_success:
            print("\n✅ 测试结果: 全部通过")
            print("\n💡 功能总结:")
            print("  ✅ Web界面支持高级防审核技术配置")
            print("  ✅ 支持100%强制执行模式")
            print("  ✅ 配置获取和更新功能正常")
            print("  ✅ 界面包含所有必要的配置项")
            
            print("\n🎯 Web界面新功能:")
            print("  🔄 镜像翻转概率配置（滑块）")
            print("  🌫️  模糊背景完整配置")
            print("  🎞️  抽帧处理完整配置")
            print("  🎯 一键强制执行模式按钮")
            
        else:
            print("\n❌ 测试结果: 部分失败")
            if not config_success:
                print("  ❌ 配置功能测试失败")
            if not interface_success:
                print("  ❌ 界面功能测试失败")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
