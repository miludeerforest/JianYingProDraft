#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试字幕编码处理优化功能
"""

import os
import tempfile
from JianYingDraft.core.srtProcessor import SRTProcessor

def create_test_srt_files():
    """创建不同编码的测试SRT文件"""
    test_files = {}
    
    # 基础SRT内容
    srt_content_utf8 = """1
00:00:01,000 --> 00:00:03,000
Hello, this is a test subtitle.

2
00:00:04,000 --> 00:00:06,000
¡Hola! Este es un subtítulo en español.

3
00:00:07,000 --> 00:00:09,000
สวัสดี นี่คือคำบรรยายภาษาไทย

4
00:00:10,000 --> 00:00:12,000
Bonjour! Ceci est un sous-titre français.

5
00:00:13,000 --> 00:00:15,000
Привет! Это русские субтитры.
"""

    # 创建不同编码的测试文件
    encodings_to_test = [
        ('utf-8', 'UTF-8编码'),
        ('utf-8-sig', 'UTF-8 BOM编码'),
        ('latin1', '西欧编码'),
        ('cp1252', 'Windows西欧编码'),
        ('cp874', '泰语编码'),
        ('cp1251', '俄语编码'),
    ]
    
    for encoding, description in encodings_to_test:
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(mode='w', encoding=encoding, 
                                                  suffix=f'_{encoding}.srt', delete=False)
            temp_file.write(srt_content_utf8)
            temp_file.close()
            
            test_files[encoding] = {
                'path': temp_file.name,
                'description': description,
                'expected_encoding': encoding
            }
            print(f"✅ 创建测试文件: {description} ({encoding})")
            
        except Exception as e:
            print(f"❌ 创建 {description} 文件失败: {e}")
    
    return test_files

def test_encoding_detection(test_files):
    """测试编码检测功能"""
    print("\n🔍 测试编码检测功能")
    print("=" * 60)
    
    processor = SRTProcessor()
    results = {}
    
    for encoding, file_info in test_files.items():
        print(f"\n📁 测试文件: {file_info['description']}")
        print(f"   原始编码: {encoding}")
        print(f"   文件路径: {os.path.basename(file_info['path'])}")
        
        try:
            # 测试编码检测
            detected_encoding = processor._detect_encoding(file_info['path'])
            
            # 测试文件读取
            content = processor._read_file_with_encoding_detection(file_info['path'])
            
            # 检查内容质量
            quality_score = processor._calculate_text_quality_score(content)
            
            results[encoding] = {
                'detected_encoding': detected_encoding,
                'quality_score': quality_score,
                'content_length': len(content),
                'success': True
            }
            
            print(f"   🎯 检测编码: {detected_encoding}")
            print(f"   📊 质量分数: {quality_score:.3f}")
            print(f"   📝 内容长度: {len(content)} 字符")
            
            # 检查是否包含特定语言字符
            has_spanish = any(c in content for c in 'ñáéíóúü¡¿')
            has_thai = any('\u0e00' <= c <= '\u0e7f' for c in content)
            has_russian = any('\u0400' <= c <= '\u04ff' for c in content)
            
            print(f"   🌍 语言检测: 西班牙语={has_spanish}, 泰语={has_thai}, 俄语={has_russian}")
            
            if quality_score > 0.7:
                print(f"   ✅ 编码处理成功")
            else:
                print(f"   ⚠️  编码处理质量较低")
                
        except Exception as e:
            print(f"   ❌ 编码处理失败: {e}")
            results[encoding] = {
                'error': str(e),
                'success': False
            }
    
    return results

def test_srt_parsing(test_files):
    """测试SRT解析功能"""
    print("\n📋 测试SRT解析功能")
    print("=" * 60)
    
    processor = SRTProcessor()
    parsing_results = {}
    
    for encoding, file_info in test_files.items():
        print(f"\n📁 解析文件: {file_info['description']}")
        
        try:
            # 解析SRT文件
            subtitles = processor.parse_srt_file(file_info['path'])
            
            parsing_results[encoding] = {
                'subtitle_count': len(subtitles),
                'success': True,
                'subtitles': subtitles[:2]  # 只保存前两个字幕用于检查
            }
            
            print(f"   📊 解析字幕数量: {len(subtitles)}")
            
            if subtitles:
                print(f"   📝 第一条字幕: {subtitles[0]['text'][:50]}...")
                print(f"   ⏱️  时长: {subtitles[0]['duration']/1000000:.1f}秒")
                
                # 检查字幕内容的语言特征
                all_text = ' '.join(sub['text'] for sub in subtitles)
                
                # 统计不同语言字符
                spanish_chars = sum(1 for c in all_text if c in 'ñáéíóúü¡¿')
                thai_chars = sum(1 for c in all_text if '\u0e00' <= c <= '\u0e7f')
                russian_chars = sum(1 for c in all_text if '\u0400' <= c <= '\u04ff')
                
                print(f"   🔤 字符统计: 西班牙语={spanish_chars}, 泰语={thai_chars}, 俄语={russian_chars}")
                
            print(f"   ✅ SRT解析成功")
            
        except Exception as e:
            print(f"   ❌ SRT解析失败: {e}")
            parsing_results[encoding] = {
                'error': str(e),
                'success': False
            }
    
    return parsing_results

def cleanup_test_files(test_files):
    """清理测试文件"""
    print("\n🧹 清理测试文件")
    for encoding, file_info in test_files.items():
        try:
            os.unlink(file_info['path'])
            print(f"   ✅ 删除: {file_info['description']}")
        except Exception as e:
            print(f"   ❌ 删除失败: {file_info['description']} - {e}")

def print_summary(detection_results, parsing_results):
    """打印测试总结"""
    print("\n📊 测试总结")
    print("=" * 60)
    
    total_tests = len(detection_results)
    successful_detections = sum(1 for r in detection_results.values() if r.get('success', False))
    successful_parsing = sum(1 for r in parsing_results.values() if r.get('success', False))
    
    print(f"📈 编码检测成功率: {successful_detections}/{total_tests} ({successful_detections/total_tests*100:.1f}%)")
    print(f"📈 SRT解析成功率: {successful_parsing}/{total_tests} ({successful_parsing/total_tests*100:.1f}%)")
    
    print(f"\n🎯 编码检测详情:")
    for encoding, result in detection_results.items():
        if result.get('success'):
            quality = result['quality_score']
            detected = result['detected_encoding']
            status = "✅" if quality > 0.7 else "⚠️"
            print(f"   {status} {encoding:12} -> {detected:12} (质量: {quality:.3f})")
        else:
            print(f"   ❌ {encoding:12} -> 失败")
    
    print(f"\n💡 优化建议:")
    print(f"   • 质量分数 > 0.8: 编码检测非常准确")
    print(f"   • 质量分数 0.6-0.8: 编码检测基本准确")
    print(f"   • 质量分数 < 0.6: 可能需要手动指定编码")

def main():
    """主函数"""
    print("🔧 字幕编码处理优化测试")
    print("=" * 60)
    print("📝 测试内容:")
    print("   • 多语言字幕文件编码检测")
    print("   • 西班牙语、泰语、俄语等小语种支持")
    print("   • SRT文件解析和质量评估")
    
    # 创建测试文件
    test_files = create_test_srt_files()
    
    if not test_files:
        print("❌ 无法创建测试文件，退出测试")
        return
    
    try:
        # 测试编码检测
        detection_results = test_encoding_detection(test_files)
        
        # 测试SRT解析
        parsing_results = test_srt_parsing(test_files)
        
        # 打印总结
        print_summary(detection_results, parsing_results)
        
    finally:
        # 清理测试文件
        cleanup_test_files(test_files)
    
    print("\n🎉 编码优化测试完成!")

if __name__ == "__main__":
    main()
