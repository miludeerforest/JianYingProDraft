#!/usr/bin/env python3
"""
剪映自动混剪工具 - Web界面启动器
快速启动Web界面的便捷脚本
"""
import os
import sys
import subprocess
import webbrowser
import time
import threading

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
        'web_interface.py',
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

def start_web_server():
    """启动Web服务器"""
    try:
        # 导入并启动Web界面
        from web_interface import app
        
        print("🌐 剪映自动混剪工具 - Web界面")
        print("=" * 50)
        print("🚀 启动Web服务器...")
        print("📱 浏览器访问: http://localhost:5000")
        print("⚙️  功能: 配置管理、排除设置、自动混剪")
        print("🔧 基于原有代码，无任何修改")
        print("=" * 50)
        print("💡 提示: 按 Ctrl+C 停止服务器")
        print()
        
        # 延迟打开浏览器
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
                print("🌐 已自动打开浏览器")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print("📱 请手动访问: http://localhost:5000")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Web服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🎬 剪映自动混剪工具 - Web界面启动器")
    print("=" * 50)
    
    # 检查依赖
    print("🔍 检查依赖包...")
    if not check_dependencies():
        return
    
    # 检查项目结构
    print("📁 检查项目结构...")
    if not check_project_structure():
        return
    
    print("✅ 所有检查通过")
    print()
    
    # 启动Web服务器
    start_web_server()

if __name__ == '__main__':
    main()
