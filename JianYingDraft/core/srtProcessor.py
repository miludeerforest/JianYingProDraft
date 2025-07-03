"""
 * @file   : srtProcessor.py
 * @time   : 19:45
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import os
import re
import chardet
from typing import List, Dict, Any, Optional, Tuple
from JianYingDraft.core.mediaText import MediaText
from JianYingDraft.core import template
from JianYingDraft.utils import tools


class SRTProcessor:
    """
    SRT字幕处理器
    实现SRT字幕文件的解析、格式修复和添加功能
    """
    
    # SRT时间戳格式的正则表达式
    SRT_TIME_PATTERN = re.compile(
        r'(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})'
    )
    
    def __init__(self):
        """初始化SRT字幕处理器"""
        self.subtitles = []  # 解析后的字幕列表
        self.encoding = 'utf-8'  # 默认编码
    
    def parse_srt_file(self, srt_path: str) -> List[Dict[str, Any]]:
        """
        解析SRT文件，提取时间戳和文本
        
        Args:
            srt_path: SRT文件路径
            
        Returns:
            List[Dict[str, Any]]: 解析后的字幕列表
        """
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"SRT文件不存在: {srt_path}")
        
        # 检测文件编码
        self.encoding = self._detect_encoding(srt_path)
        
        try:
            with open(srt_path, 'r', encoding=self.encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果检测的编码失败，尝试常见编码
            for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
                try:
                    with open(srt_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError(f"无法解码SRT文件: {srt_path}")
        
        # 自动修复SRT格式错误
        content = self._auto_fix_srt_format(content)

        # 解析SRT内容
        self.subtitles = self._parse_srt_content(content)
        return self.subtitles
    
    def _parse_srt_content(self, content: str) -> List[Dict[str, Any]]:
        """
        解析SRT内容
        
        Args:
            content: SRT文件内容
            
        Returns:
            List[Dict[str, Any]]: 解析后的字幕列表
        """
        subtitles = []
        
        # 按空行分割字幕块
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                # 第一行：序号
                index = int(lines[0].strip())
                
                # 第二行：时间戳
                time_line = lines[1].strip()
                time_match = self.SRT_TIME_PATTERN.match(time_line)
                
                if not time_match:
                    print(f"警告：无法解析时间戳: {time_line}")
                    continue
                
                # 解析开始和结束时间
                start_time = self._time_to_microseconds(*time_match.groups()[:4])
                end_time = self._time_to_microseconds(*time_match.groups()[4:8])
                
                # 第三行及以后：字幕文本
                text = '\n'.join(lines[2:]).strip()
                
                # 清理文本
                text = self._clean_subtitle_text(text)
                
                subtitle = {
                    'index': index,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'text': text,
                    'original_text': '\n'.join(lines[2:]).strip()
                }
                
                subtitles.append(subtitle)
                
            except (ValueError, IndexError) as e:
                print(f"警告：解析字幕块失败: {e}")
                continue
        
        return subtitles

    def _auto_fix_srt_format(self, content: str) -> str:
        """
        自动修复SRT格式错误

        Args:
            content: 原始SRT内容

        Returns:
            str: 修复后的SRT内容
        """
        print("🔧 开始SRT格式自动修复...")

        # 记录修复的问题
        fixes_applied = []

        # 1. 统一换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        fixes_applied.append("统一换行符")

        # 2. 移除BOM标记
        if content.startswith('\ufeff'):
            content = content[1:]
            fixes_applied.append("移除BOM标记")

        # 3. 修复时间戳格式
        content = self._fix_timestamp_format(content, fixes_applied)

        # 4. 修复序号问题
        content = self._fix_subtitle_numbering(content, fixes_applied)

        # 5. 修复空行问题
        content = self._fix_empty_lines(content, fixes_applied)

        # 6. 修复文本编码问题
        content = self._fix_text_encoding(content, fixes_applied)

        # 7. 修复时间重叠问题
        content = self._fix_time_overlaps(content, fixes_applied)

        # 8. 移除无效字符
        content = self._remove_invalid_characters(content, fixes_applied)

        # 输出修复报告
        if fixes_applied:
            print(f"  ✅ 应用了 {len(fixes_applied)} 项修复:")
            for fix in fixes_applied:
                print(f"    • {fix}")
        else:
            print("  ✅ SRT格式正常，无需修复")

        return content

    def _fix_timestamp_format(self, content: str, fixes_applied: List[str]) -> str:
        """修复时间戳格式问题"""
        original_content = content

        # 1. 修复时间单位错误（秒被错写成分钟）
        content = self._fix_time_unit_errors(content, fixes_applied)

        # 2. 修复时间戳分隔符（统一使用逗号）
        content = re.sub(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', r'\1:\2:\3,\4', content)

        # 3. 修复箭头格式（统一使用 --> ）
        content = re.sub(r'(\d{2}:\d{2}:\d{2},\d{3})\s*[-=]+>\s*(\d{2}:\d{2}:\d{2},\d{3})', r'\1 --> \2', content)

        # 4. 修复单位数小时（补零）
        content = re.sub(r'(\n|^)(\d):(\d{2}:\d{2},\d{3})', r'\g<1>0\2:\3', content)

        # 5. 修复缺失毫秒的时间戳
        content = re.sub(r'(\d{2}:\d{2}:\d{2})\s*-->\s*(\d{2}:\d{2}:\d{2})(?!\d)', r'\1,000 --> \2,000', content)

        if content != original_content:
            fixes_applied.append("修复时间戳格式")

        return content

    def _fix_time_unit_errors(self, content: str, fixes_applied: List[str]) -> str:
        """修复时间单位错误（秒被错写成分钟格式）"""
        lines = content.split('\n')
        fixed_lines = []

        for line in lines:
            original_line = line

            # 检查是否是时间戳行
            if '-->' in line:
                # 检测可能的时间单位错误
                line = self._detect_and_fix_time_units(line, fixes_applied)

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def _detect_and_fix_time_units(self, timestamp_line: str, fixes_applied: List[str]) -> str:
        """检测并修复时间单位错误"""
        # 匹配时间戳格式：HH:MM:SS,mmm --> HH:MM:SS,mmm
        time_pattern = r'(\d{1,2}):(\d{1,2}):(\d{1,2})[,.](\d{1,3})\s*-->\s*(\d{1,2}):(\d{1,2}):(\d{1,2})[,.](\d{1,3})'
        match = re.search(time_pattern, timestamp_line)

        if not match:
            return timestamp_line

        # 提取时间组件
        start_h, start_m, start_s, start_ms = match.groups()[:4]
        end_h, end_m, end_s, end_ms = match.groups()[4:]

        # 检测时间单位错误的模式
        fixed = False

        # 模式1: 秒数超过59，可能是秒被当作分钟写了
        # 例如：00:01:90,000 应该是 00:02:30,000
        if int(start_s) >= 60:
            extra_minutes = int(start_s) // 60
            new_seconds = int(start_s) % 60
            new_minutes = int(start_m) + extra_minutes

            if new_minutes >= 60:
                extra_hours = new_minutes // 60
                new_minutes = new_minutes % 60
                start_h = str(int(start_h) + extra_hours).zfill(2)

            start_m = str(new_minutes).zfill(2)
            start_s = str(new_seconds).zfill(2)
            fixed = True

        if int(end_s) >= 60:
            extra_minutes = int(end_s) // 60
            new_seconds = int(end_s) % 60
            new_minutes = int(end_m) + extra_minutes

            if new_minutes >= 60:
                extra_hours = new_minutes // 60
                new_minutes = new_minutes % 60
                end_h = str(int(end_h) + extra_hours).zfill(2)

            end_m = str(new_minutes).zfill(2)
            end_s = str(new_seconds).zfill(2)
            fixed = True

        # 模式2: 分钟数超过59，可能是分钟被当作秒写了
        # 例如：00:90:30,000 应该是 01:30:30,000
        if int(start_m) >= 60:
            extra_hours = int(start_m) // 60
            new_minutes = int(start_m) % 60
            start_h = str(int(start_h) + extra_hours).zfill(2)
            start_m = str(new_minutes).zfill(2)
            fixed = True

        if int(end_m) >= 60:
            extra_hours = int(end_m) // 60
            new_minutes = int(end_m) % 60
            end_h = str(int(end_h) + extra_hours).zfill(2)
            end_m = str(new_minutes).zfill(2)
            fixed = True

        # 模式3: 检测异常的时间跨度（可能是单位错误）
        # 例如：00:01:30,000 --> 00:01:90,000 (90秒应该是1分30秒)
        start_total_seconds = int(start_h) * 3600 + int(start_m) * 60 + int(start_s)
        end_total_seconds = int(end_h) * 3600 + int(end_m) * 60 + int(end_s)
        duration = end_total_seconds - start_total_seconds

        # 如果持续时间异常长（超过10分钟），可能是单位错误
        if duration > 600:  # 10分钟
            # 检查是否是秒数被当作分钟的情况
            # 例如：00:01:30 --> 00:05:30 (4分钟) 可能应该是 00:01:30 --> 00:01:34 (4秒)
            if duration < 3600 and int(end_s) > int(start_s):  # 小于1小时且结束秒数大于开始秒数
                # 尝试将分钟差转换为秒差
                minute_diff = int(end_m) - int(start_m)
                if minute_diff > 0 and minute_diff < 60:
                    new_end_s = int(start_s) + minute_diff
                    if new_end_s < 60:
                        end_m = start_m
                        end_s = str(new_end_s).zfill(2)
                        fixed = True

        # 模式4: 检测分钟位置实际是秒数的错误
        # 例如：00:03:00,800 应该是 00:00:03,800 (3秒，不是3分钟)
        # 特征：分钟数较小(通常<60)，但秒数为00

        # 检查开始时间：如果分钟位>0且秒位=0，且分钟位<60，很可能是分钟位实际是秒数
        if (int(start_m) > 0 and int(start_s) == 0 and int(start_m) < 60):
            # 将分钟位的值移到秒位，分钟位设为0
            new_start_s = start_m
            new_start_m = "00"

            # 如果原来的分钟位值超过59，需要进一步转换
            if int(new_start_s) >= 60:
                extra_minutes = int(new_start_s) // 60
                new_start_s = str(int(new_start_s) % 60).zfill(2)
                new_start_m = str(extra_minutes).zfill(2)
            else:
                new_start_s = str(int(new_start_s)).zfill(2)

            start_m = new_start_m
            start_s = new_start_s
            fixed = True

        # 检查结束时间：如果分钟位>0且秒位=0，且分钟位<60，很可能是分钟位实际是秒数
        if (int(end_m) > 0 and int(end_s) == 0 and int(end_m) < 60):
            # 将分钟位的值移到秒位，分钟位设为0
            new_end_s = end_m
            new_end_m = "00"

            # 如果原来的分钟位值超过59，需要进一步转换
            if int(new_end_s) >= 60:
                extra_minutes = int(new_end_s) // 60
                new_end_s = str(int(new_end_s) % 60).zfill(2)
                new_end_m = str(extra_minutes).zfill(2)
            else:
                new_end_s = str(int(new_end_s)).zfill(2)

            end_m = new_end_m
            end_s = new_end_s
            fixed = True

        # 模式5: 检测明显的错误模式
        # 例如：00:00:90,000 --> 00:00:120,000
        if int(start_s) >= 60 or int(end_s) >= 60:
            # 已在模式1中处理
            pass

        if fixed:
            # 重新构建时间戳
            start_ms = start_ms.ljust(3, '0')[:3]  # 确保毫秒是3位
            end_ms = end_ms.ljust(3, '0')[:3]

            new_timestamp = f"{start_h}:{start_m}:{start_s},{start_ms} --> {end_h}:{end_m}:{end_s},{end_ms}"

            # 替换原时间戳
            fixed_line = re.sub(time_pattern, new_timestamp, timestamp_line)

            if "修复时间单位错误" not in fixes_applied:
                fixes_applied.append("修复时间单位错误")

            return fixed_line

        return timestamp_line

    def _fix_subtitle_numbering(self, content: str, fixes_applied: List[str]) -> str:
        """修复字幕序号问题"""
        lines = content.split('\n')
        fixed_lines = []
        current_number = 1
        in_subtitle_block = False
        block_lines = []

        for line in lines:
            line = line.strip()

            # 检查是否是时间戳行
            if self.SRT_TIME_PATTERN.match(line):
                if block_lines:
                    # 处理前一个字幕块
                    if not block_lines[0].isdigit():
                        block_lines.insert(0, str(current_number))
                        fixes_applied.append("修复缺失序号")
                    else:
                        block_lines[0] = str(current_number)

                    fixed_lines.extend(block_lines)
                    current_number += 1
                    block_lines = []

                block_lines.append(line)
                in_subtitle_block = True
            elif line == '':
                if block_lines:
                    fixed_lines.extend(block_lines)
                    fixed_lines.append('')
                    block_lines = []
                in_subtitle_block = False
            else:
                if in_subtitle_block or (line.isdigit() and not block_lines):
                    block_lines.append(line)
                else:
                    fixed_lines.append(line)

        # 处理最后一个字幕块
        if block_lines:
            if not block_lines[0].isdigit():
                block_lines.insert(0, str(current_number))
                fixes_applied.append("修复缺失序号")
            else:
                block_lines[0] = str(current_number)
            fixed_lines.extend(block_lines)

        return '\n'.join(fixed_lines)

    def _fix_empty_lines(self, content: str, fixes_applied: List[str]) -> str:
        """修复空行问题"""
        original_content = content

        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 确保字幕块之间有空行
        content = re.sub(r'(\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n[^\n]+)\n(\d+)', r'\1\n\n\2', content)

        # 移除开头和结尾的空行
        content = content.strip()

        if content != original_content:
            fixes_applied.append("修复空行问题")

        return content

    def _fix_text_encoding(self, content: str, fixes_applied: List[str]) -> str:
        """修复文本编码问题"""
        original_content = content

        # 修复常见的编码问题
        encoding_fixes = {
            'â€™': "'",  # 单引号
            'â€œ': '"',  # 左双引号
            'â€': '"',   # 右双引号
            'â€"': '—',  # 长破折号
            'â€"': '–',  # 短破折号
            'â€¦': '…',  # 省略号
            'Ã¡': 'á',   # 带重音的a
            'Ã©': 'é',   # 带重音的e
            'Ã­': 'í',   # 带重音的i
            'Ã³': 'ó',   # 带重音的o
            'Ãº': 'ú',   # 带重音的u
        }

        for wrong, correct in encoding_fixes.items():
            if wrong in content:
                content = content.replace(wrong, correct)
                fixes_applied.append(f"修复编码问题: {wrong} → {correct}")

        return content

    def _fix_time_overlaps(self, content: str, fixes_applied: List[str]) -> str:
        """修复时间重叠问题"""
        lines = content.split('\n')
        fixed_lines = []
        last_end_time = 0

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 检查时间戳行
            time_match = self.SRT_TIME_PATTERN.match(line)
            if time_match:
                start_time = self._time_to_microseconds(*time_match.groups()[:4])
                end_time = self._time_to_microseconds(*time_match.groups()[4:8])

                # 检查时间重叠
                if start_time < last_end_time:
                    # 调整开始时间
                    start_time = last_end_time + 100000  # 加100毫秒间隔

                    # 重新格式化时间戳
                    start_formatted = self._microseconds_to_srt_time(start_time)
                    end_formatted = self._microseconds_to_srt_time(end_time)
                    line = f"{start_formatted} --> {end_formatted}"

                    fixes_applied.append("修复时间重叠")

                last_end_time = end_time

            fixed_lines.append(lines[i])
            i += 1

        return '\n'.join(fixed_lines)

    def _remove_invalid_characters(self, content: str, fixes_applied: List[str]) -> str:
        """移除无效字符"""
        original_content = content

        # 移除控制字符（除了换行符和制表符）
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)

        # 移除HTML标签（如果存在）
        content = re.sub(r'<[^>]+>', '', content)

        # 移除多余的空格
        content = re.sub(r'[ \t]+', ' ', content)

        if content != original_content:
            fixes_applied.append("移除无效字符")

        return content

    def _microseconds_to_srt_time(self, microseconds: int) -> str:
        """将微秒转换为SRT时间格式"""
        total_seconds = microseconds // 1000000
        milliseconds = (microseconds % 1000000) // 1000

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def _time_to_microseconds(self, hours: str, minutes: str, seconds: str, milliseconds: str) -> int:
        """
        将SRT时间戳转换为微秒
        
        Args:
            hours: 小时
            minutes: 分钟
            seconds: 秒
            milliseconds: 毫秒
            
        Returns:
            int: 微秒数
        """
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        total_microseconds = total_seconds * 1000000 + int(milliseconds) * 1000
        return total_microseconds
    
    def _clean_subtitle_text(self, text: str) -> str:
        """
        清理字幕文本
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    def fix_srt_format(self, subtitles: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        修复SRT格式问题
        
        Args:
            subtitles: 字幕列表，如果为None则使用当前解析的字幕
            
        Returns:
            List[Dict[str, Any]]: 修复后的字幕列表
        """
        if subtitles is None:
            subtitles = self.subtitles
        
        if not subtitles:
            return []
        
        fixed_subtitles = []
        
        for i, subtitle in enumerate(subtitles):
            fixed_subtitle = subtitle.copy()
            
            # 修复时间戳重叠问题
            if i > 0:
                prev_subtitle = fixed_subtitles[-1]
                if fixed_subtitle['start_time'] < prev_subtitle['end_time']:
                    # 当前字幕开始时间早于前一个字幕结束时间，调整前一个字幕的结束时间
                    prev_subtitle['end_time'] = fixed_subtitle['start_time']
                    prev_subtitle['duration'] = prev_subtitle['end_time'] - prev_subtitle['start_time']
                    
                    # 如果调整后时长过短，删除前一个字幕
                    if prev_subtitle['duration'] < 100000:  # 小于0.1秒
                        fixed_subtitles.pop()
            
            # 确保字幕时长合理
            min_duration = 500000  # 最小0.5秒
            max_duration = 10000000  # 最大10秒
            
            if fixed_subtitle['duration'] < min_duration:
                fixed_subtitle['end_time'] = fixed_subtitle['start_time'] + min_duration
                fixed_subtitle['duration'] = min_duration
            elif fixed_subtitle['duration'] > max_duration:
                fixed_subtitle['end_time'] = fixed_subtitle['start_time'] + max_duration
                fixed_subtitle['duration'] = max_duration
            
            # 确保文本不为空
            if not fixed_subtitle['text'].strip():
                continue
            
            # 限制文本长度
            if len(fixed_subtitle['text']) > 100:
                fixed_subtitle['text'] = fixed_subtitle['text'][:97] + '...'
            
            fixed_subtitles.append(fixed_subtitle)
        
        return fixed_subtitles
    
    def optimize_subtitle_timing(self, subtitles: List[Dict[str, Any]], video_duration: int) -> List[Dict[str, Any]]:
        """
        优化字幕时间分配
        
        Args:
            subtitles: 字幕列表
            video_duration: 视频总时长（微秒）
            
        Returns:
            List[Dict[str, Any]]: 优化后的字幕列表
        """
        if not subtitles:
            return []
        
        optimized_subtitles = []
        
        for subtitle in subtitles:
            optimized_subtitle = subtitle.copy()
            
            # 确保字幕不超出视频时长
            if optimized_subtitle['start_time'] >= video_duration:
                break
            
            if optimized_subtitle['end_time'] > video_duration:
                optimized_subtitle['end_time'] = video_duration
                optimized_subtitle['duration'] = optimized_subtitle['end_time'] - optimized_subtitle['start_time']
                
                # 如果调整后时长过短，跳过这个字幕
                if optimized_subtitle['duration'] < 100000:  # 小于0.1秒
                    break
            
            optimized_subtitles.append(optimized_subtitle)
        
        return optimized_subtitles
    
    def create_subtitle_segments(self, subtitles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        创建字幕片段
        
        Args:
            subtitles: 字幕列表
            
        Returns:
            List[Dict[str, Any]]: 字幕片段列表
        """
        segments = []
        
        for subtitle in subtitles:
            # 创建MediaText实例
            media_text = MediaText(
                text=subtitle['text'],
                duration=subtitle['duration'],
                color="#FFFFFF"
            )
            
            # 创建字幕片段
            segment = media_text.segment_data_for_content.copy()
            
            # 设置时间范围
            segment['target_timerange'] = {
                'start': subtitle['start_time'],
                'duration': subtitle['duration']
            }
            
            # 设置字幕位置（底部居中）
            if 'clip' not in segment:
                segment['clip'] = {
                    "alpha": 1.0,
                    "flip": {"horizontal": False, "vertical": False},
                    "rotation": 0.0,
                    "scale": {"x": 1.0, "y": 1.0},
                    "transform": {"x": 0.0, "y": -0.8}  # 底部位置
                }
            else:
                segment['clip']['transform']['y'] = -0.8
            
            segments.append({
                'segment': segment,
                'material': media_text.material_data_for_content,
                'subtitle_info': subtitle
            })
        
        return segments
    
    def add_subtitles_to_draft(self, draft, subtitles: List[Dict[str, Any]]) -> int:
        """
        批量添加字幕到草稿
        
        Args:
            draft: 草稿对象
            subtitles: 字幕列表
            
        Returns:
            int: 成功添加的字幕数量
        """
        success_count = 0
        
        for i, subtitle in enumerate(subtitles):
            try:
                draft.add_subtitle(
                    subtitle=subtitle['text'],
                    color="#FFFFFF",
                    start_at_track=0,  # 统一使用轨道0
                    duration=subtitle['duration'],
                    index=i,
                    start=subtitle['start_time']
                )
                success_count += 1
            except Exception as e:
                print(f"添加字幕失败: {subtitle['text'][:20]}... - {str(e)}")
                continue
        
        return success_count
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 检测到的编码
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
                
                # 处理一些特殊情况
                if encoding and encoding.lower().startswith('gb'):
                    return 'gbk'
                elif encoding and 'utf' in encoding.lower():
                    return 'utf-8'
                else:
                    return encoding or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        获取处理摘要
        
        Returns:
            Dict[str, Any]: 处理摘要信息
        """
        if not self.subtitles:
            return {
                'total_subtitles': 0,
                'total_duration': 0,
                'average_duration': 0,
                'encoding': self.encoding
            }
        
        total_duration = sum(sub['duration'] for sub in self.subtitles)
        average_duration = total_duration / len(self.subtitles) if self.subtitles else 0
        
        return {
            'total_subtitles': len(self.subtitles),
            'total_duration': total_duration,
            'average_duration': average_duration,
            'encoding': self.encoding,
            'first_subtitle_time': self.subtitles[0]['start_time'] if self.subtitles else 0,
            'last_subtitle_time': self.subtitles[-1]['end_time'] if self.subtitles else 0
        }
    
    def print_processing_summary(self):
        """打印处理摘要"""
        summary = self.get_processing_summary()
        
        print("=== SRT字幕处理摘要 ===")
        print(f"字幕总数: {summary['total_subtitles']}")
        print(f"总时长: {summary['total_duration']/1000000:.1f}s")
        print(f"平均时长: {summary['average_duration']/1000000:.1f}s")
        print(f"文件编码: {summary['encoding']}")
        
        if summary['total_subtitles'] > 0:
            print(f"首个字幕: {summary['first_subtitle_time']/1000000:.1f}s")
            print(f"最后字幕: {summary['last_subtitle_time']/1000000:.1f}s")
        
        print("=====================")
