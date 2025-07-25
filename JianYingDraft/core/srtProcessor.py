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
from typing import List, Dict, Any, Optional
from JianYingDraft.core.mediaText import MediaText

# 尝试导入chardet，如果没有则使用内置方法
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    print("⚠️  chardet库未安装，将使用内置编码检测方法")


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

        # 简单读取文件，不进行编码检测和内容修改
        content = self._simple_read_file(srt_path)

        # 解析SRT内容（不修改内容）
        self.subtitles = self._parse_srt_content(content)
        return self.subtitles

    def _simple_read_file(self, file_path: str) -> str:
        """
        简单读取文件，不进行编码检测和内容修改

        Args:
            file_path: 文件路径

        Returns:
            str: 文件内容
        """
        # 尝试常见编码，按优先级顺序
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'latin1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"  ✅ 使用编码 {encoding} 读取成功")
                return content
            except (UnicodeDecodeError, UnicodeError):
                continue

        # 如果所有编码都失败，使用latin1（不会失败）
        with open(file_path, 'r', encoding='latin1') as f:
            content = f.read()
        print(f"  ⚠️ 使用备用编码 latin1 读取")
        return content

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
                # 智能解析字幕块结构
                index = None
                time_line = None
                text_lines = []

                # 查找序号行和时间戳行
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue

                    # 尝试解析序号
                    if index is None and line.isdigit():
                        index = int(line)
                        continue

                    # 尝试解析时间戳
                    if time_line is None and self.SRT_TIME_PATTERN.match(line):
                        time_line = line
                        continue

                    # 其余为文本内容
                    if index is not None and time_line is not None:
                        text_lines.append(line)

                # 验证必要信息
                if index is None:
                    print(f"警告：字幕块缺少序号: {lines[0][:50]}...")
                    continue

                if time_line is None:
                    print(f"警告：字幕块缺少时间戳: {' | '.join(lines[:3])}")
                    continue

                time_match = self.SRT_TIME_PATTERN.match(time_line)
                if not time_match:
                    print(f"警告：无法解析时间戳格式: {time_line}")
                    continue
                
                # 解析开始和结束时间
                start_time = self._time_to_microseconds(*time_match.groups()[:4])
                end_time = self._time_to_microseconds(*time_match.groups()[4:8])
                
                # 组合字幕文本，不进行任何内容修改
                text = '\n'.join(text_lines).strip()
                
                subtitle = {
                    'index': index,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'text': text,
                    'original_text': '\n'.join(text_lines).strip()
                }
                
                subtitles.append(subtitle)
                
            except (ValueError, IndexError) as e:
                print(f"警告：解析字幕块失败: {e}")
                continue
        
        return subtitles

    def _auto_fix_srt_format(self, content: str) -> str:
        """
        自动修复SRT格式错误 - 只修复时间戳，不修改字幕文本内容

        Args:
            content: 原始SRT内容

        Returns:
            str: 修复后的SRT内容
        """
        print("🔧 开始SRT时间戳修复（保留原始字幕内容）...")

        # 记录修复的问题
        fixes_applied = []

        # 1. 统一换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        fixes_applied.append("统一换行符")

        # 2. 移除BOM标记
        if content.startswith('\ufeff'):
            content = content[1:]
            fixes_applied.append("移除BOM标记")

        # 3. 只修复时间戳格式，不修改字幕文本
        content = self._fix_timestamp_only(content, fixes_applied)

        # 4. 修复序号问题（不涉及文本内容）
        content = self._fix_subtitle_numbering(content, fixes_applied)

        # 5. 修复空行问题（不涉及文本内容）
        content = self._fix_empty_lines(content, fixes_applied)

        # 输出修复报告
        if fixes_applied:
            print(f"  ✅ 应用了 {len(fixes_applied)} 项修复:")
            for fix in fixes_applied:
                print(f"    • {fix}")
        else:
            print("  ✅ SRT格式正常，无需修复")

        return content

    def _fix_timestamp_only(self, content: str, fixes_applied: List[str]) -> str:
        """
        只修复时间戳格式，完全不修改字幕文本内容

        Args:
            content: 原始SRT内容
            fixes_applied: 修复记录列表

        Returns:
            str: 只修复时间戳的SRT内容
        """
        lines = content.split('\n')
        fixed_lines = []
        timestamp_fixes = 0

        for line in lines:
            # 只处理包含时间戳的行（包含 --> 的行）
            if '-->' in line:
                original_line = line
                fixed_line = self._fix_single_timestamp_line(line)

                if fixed_line != original_line:
                    timestamp_fixes += 1
                    print(f"    🕐 时间戳修复: {original_line.strip()} → {fixed_line.strip()}")

                fixed_lines.append(fixed_line)
            else:
                # 非时间戳行完全保持原样，不做任何修改
                fixed_lines.append(line)

        if timestamp_fixes > 0:
            fixes_applied.append(f"修复时间戳格式 ({timestamp_fixes}处)")

        return '\n'.join(fixed_lines)

    def _fix_single_timestamp_line(self, line: str) -> str:
        """
        修复单行时间戳格式

        Args:
            line: 时间戳行

        Returns:
            str: 修复后的时间戳行
        """
        # 保存行首和行尾的空白字符
        leading_space = len(line) - len(line.lstrip())
        trailing_space = len(line) - len(line.rstrip())

        # 获取核心内容
        core_content = line.strip()

        # 1. 修复时间单位错误（秒被错写成分钟）
        # 例如：00:03:00,800 → 00:00:03,800
        core_content = self._fix_time_unit_in_line(core_content)

        # 2. 修复时间戳分隔符（统一使用逗号）
        # 例如：00:00:03.800 → 00:00:03,800
        core_content = re.sub(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', r'\1:\2:\3,\4', core_content)

        # 3. 修复箭头格式（统一使用 --> ）
        # 例如：00:00:03,800 -> 00:00:06,800 → 00:00:03,800 --> 00:00:06,800
        core_content = re.sub(r'(\d{2}:\d{2}:\d{2},\d{3})\s*[-=]+>\s*(\d{2}:\d{2}:\d{2},\d{3})', r'\1 --> \2', core_content)

        # 4. 修复单位数小时（补零）
        # 例如：1:00:03,800 → 01:00:03,800
        core_content = re.sub(r'^(\d):(\d{2}:\d{2},\d{3})', r'0\1:\2', core_content)
        core_content = re.sub(r'-->\s*(\d):(\d{2}:\d{2},\d{3})', r'--> 0\1:\2', core_content)

        # 5. 修复缺失毫秒的时间戳
        # 例如：00:00:03 --> 00:00:06 → 00:00:03,000 --> 00:00:06,000
        core_content = re.sub(r'(\d{2}:\d{2}:\d{2})\s*-->\s*(\d{2}:\d{2}:\d{2})(?!\d)', r'\1,000 --> \2,000', core_content)

        # 6. 确保箭头前后有空格
        core_content = re.sub(r'(\d{2}:\d{2}:\d{2},\d{3})-->', r'\1 -->', core_content)
        core_content = re.sub(r'-->(\d{2}:\d{2}:\d{2},\d{3})', r'--> \1', core_content)

        # 恢复原始的空白字符
        return ' ' * leading_space + core_content + ' ' * trailing_space

    def _fix_time_unit_in_line(self, line: str) -> str:
        """
        修复时间单位错误（秒被错写成分钟）

        Args:
            line: 时间戳行

        Returns:
            str: 修复后的时间戳行
        """
        # 匹配时间戳格式：HH:MM:SS,mmm
        timestamp_pattern = r'(\d{2}):(\d{2}):(\d{2}),(\d{3})'

        def fix_timestamp(match):
            hours, minutes, seconds, milliseconds = match.groups()
            hours, minutes, seconds = int(hours), int(minutes), int(seconds)

            # 检查是否存在时间单位错误
            # 如果秒数大于59，可能是被错写成分钟了
            if seconds > 59:
                # 将秒数转换为分钟和秒
                extra_minutes = seconds // 60
                actual_seconds = seconds % 60

                # 将额外的分钟加到分钟位
                minutes += extra_minutes

                # 如果分钟数大于59，转换为小时
                if minutes > 59:
                    extra_hours = minutes // 60
                    minutes = minutes % 60
                    hours += extra_hours

                # 确保小时不超过23
                hours = min(hours, 23)

                return f"{hours:02d}:{minutes:02d}:{actual_seconds:02d},{milliseconds}"

            return match.group(0)  # 无需修复，返回原始内容

        return re.sub(timestamp_pattern, fix_timestamp, line)

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
        简化字幕时间轴处理：只做时长裁剪，不修改内容

        Args:
            subtitles: 字幕列表
            video_duration: 视频总时长（微秒）

        Returns:
            List[Dict[str, Any]]: 处理后的字幕列表
        """
        if not subtitles:
            return []

        processed_subtitles = []

        for subtitle in subtitles:
            # 如果字幕开始时间超出视频时长，直接跳过
            if subtitle['start_time'] >= video_duration:
                break

            # 复制字幕数据，不修改原始内容
            processed_subtitle = subtitle.copy()

            # 如果字幕结束时间超出视频时长，直接裁剪到视频结束
            if processed_subtitle['end_time'] > video_duration:
                processed_subtitle['end_time'] = video_duration
                processed_subtitle['duration'] = video_duration - processed_subtitle['start_time']

                # 如果裁剪后时长太短（小于0.5秒），跳过这个字幕
                if processed_subtitle['duration'] < 500000:
                    break

            processed_subtitles.append(processed_subtitle)

        return processed_subtitles
    
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
        智能检测文件编码，优先级：BOM检测 > chardet检测 > 实际测试

        Args:
            file_path: 文件路径

        Returns:
            str: 检测到的编码
        """
        try:
            # 读取文件的前几个字节检测BOM
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB

            # 检测BOM标记
            if raw_data.startswith(b'\xef\xbb\xbf'):
                print(f"  📝 检测到UTF-8 BOM编码")
                return 'utf-8-sig'
            elif raw_data.startswith(b'\xff\xfe'):
                print(f"  📝 检测到UTF-16 LE编码")
                return 'utf-16-le'
            elif raw_data.startswith(b'\xfe\xff'):
                print(f"  📝 检测到UTF-16 BE编码")
                return 'utf-16-be'

            # 使用chardet检测编码（如果可用）
            if HAS_CHARDET:
                result = chardet.detect(raw_data)
                detected_encoding = result.get('encoding', '').lower()
                confidence = result.get('confidence', 0)

                print(f"  📝 chardet检测结果: {detected_encoding} (置信度: {confidence:.2f})")

                # 根据检测结果和置信度选择编码，优化小语种支持
                if confidence > 0.7:  # 降低置信度阈值，给更多编码机会
                    # 高置信度，使用检测结果
                    if 'utf-8' in detected_encoding:
                        return 'utf-8'
                    elif detected_encoding.startswith('gb') or 'chinese' in detected_encoding:
                        return 'gbk'
                    elif 'big5' in detected_encoding:
                        return 'big5'
                    elif detected_encoding.startswith('iso-8859'):
                        # 根据具体的ISO编码选择最佳匹配
                        if 'iso-8859-1' in detected_encoding:
                            return 'latin1'
                        elif 'iso-8859-11' in detected_encoding:
                            return 'iso-8859-11'  # 泰语
                        else:
                            return detected_encoding
                    elif 'cp874' in detected_encoding or 'tis-620' in detected_encoding:
                        return 'cp874'  # 泰语Windows编码
                    elif 'cp1252' in detected_encoding:
                        return 'cp1252'  # Windows西欧编码
                    elif 'cp1251' in detected_encoding:
                        return 'cp1251'  # Windows西里尔编码
                    elif 'cp1250' in detected_encoding:
                        return 'cp1250'  # Windows中欧编码
                    elif 'shift_jis' in detected_encoding or 'sjis' in detected_encoding:
                        return 'shift_jis'  # 日语编码
                    elif 'euc-kr' in detected_encoding:
                        return 'euc-kr'  # 韩语编码
                    elif 'koi8-r' in detected_encoding:
                        return 'koi8-r'  # 俄语编码
                    else:
                        return detected_encoding
                elif confidence > 0.3:
                    # 中等置信度，结合检测结果和实际测试
                    print(f"  🔍 中等置信度，结合检测结果进行测试")
                    return self._test_encoding_with_hint(raw_data, detected_encoding)
                else:
                    # 低置信度，先检查是否为泰语，再使用实际测试方法
                    thai_encoding = self._detect_thai_encoding_special(raw_data)
                    if thai_encoding:
                        return thai_encoding
                    return self._test_encoding_by_trial(raw_data)
            else:
                # 没有chardet，直接使用实际测试方法
                print(f"  📝 使用内置编码检测方法")
                return self._test_encoding_by_trial(raw_data)

        except Exception as e:
            print(f"  ⚠️  编码检测异常: {str(e)}")
            return 'utf-8'

    def _test_encoding_by_trial(self, raw_data: bytes) -> str:
        """
        通过实际尝试解码来确定最佳编码，优化小语种支持

        Args:
            raw_data: 原始字节数据

        Returns:
            str: 最佳编码
        """
        # 扩展的编码优先级列表，增加小语种支持
        encodings_to_try = [
            'utf-8',           # 最常见的现代编码
            'utf-8-sig',       # 带BOM的UTF-8

            # 中文编码
            'gbk',             # 中文Windows默认编码
            'gb2312',          # 简体中文编码
            'big5',            # 繁体中文编码

            # 西欧语言编码（西班牙语、法语、德语等）
            'latin1',          # ISO-8859-1 西欧编码
            'iso-8859-1',      # 同latin1
            'cp1252',          # Windows西欧编码
            'iso-8859-15',     # 西欧编码（包含欧元符号）

            # 东欧语言编码
            'cp1250',          # Windows中欧编码
            'iso-8859-2',      # 中欧编码

            # 西里尔字母编码（俄语等）
            'cp1251',          # Windows西里尔编码
            'iso-8859-5',      # 西里尔编码
            'koi8-r',          # 俄语编码

            # 希腊语编码
            'cp1253',          # Windows希腊语编码
            'iso-8859-7',      # 希腊语编码

            # 土耳其语编码
            'cp1254',          # Windows土耳其语编码
            'iso-8859-9',      # 土耳其语编码

            # 泰语编码
            'cp874',           # Windows泰语编码
            'iso-8859-11',     # 泰语编码（TIS-620）
            'tis-620',         # 泰语标准编码

            # 阿拉伯语编码
            'cp1256',          # Windows阿拉伯语编码
            'iso-8859-6',      # 阿拉伯语编码

            # 希伯来语编码
            'cp1255',          # Windows希伯来语编码
            'iso-8859-8',      # 希伯来语编码

            # 日语编码
            'shift_jis',       # 日语Shift-JIS编码
            'euc-jp',          # 日语EUC编码
            'iso-2022-jp',     # 日语ISO编码

            # 韩语编码
            'euc-kr',          # 韩语EUC编码
            'cp949',           # 韩语Windows编码

            # 其他常见编码
            'ascii',           # 纯ASCII编码
            'cp437',           # DOS编码
            'cp850',           # DOS多语言编码
        ]

        best_encoding = 'utf-8'
        best_score = 0

        for encoding in encodings_to_try:
            try:
                # 尝试解码
                decoded_text = raw_data.decode(encoding)

                # 计算解码质量分数
                score = self._calculate_text_quality_score(decoded_text)

                print(f"    🔍 测试编码 {encoding}: 分数 {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_encoding = encoding

                # 如果分数很高，直接使用
                if score > 0.9:
                    break

            except (UnicodeDecodeError, UnicodeError):
                print(f"    ❌ 编码 {encoding} 解码失败")
                continue

        print(f"  ✅ 选择最佳编码: {best_encoding} (分数: {best_score:.2f})")
        return best_encoding

    def _detect_thai_encoding_special(self, raw_data: bytes) -> str:
        """
        专门检测泰语编码

        Args:
            raw_data: 原始字节数据

        Returns:
            str: 泰语编码或None
        """
        print(f"  🇹🇭 专门检测泰语编码...")

        # 首先检查是否包含泰语UTF-8字节模式
        if self._has_thai_utf8_pattern(raw_data):
            print(f"    🔍 检测到泰语UTF-8字节模式")
            try:
                decoded_text = raw_data.decode('utf-8')
                thai_char_count = sum(1 for char in decoded_text if '\u0E00' <= char <= '\u0E7F')
                if thai_char_count > 0:
                    print(f"    ✅ 确认为UTF-8泰语文本")
                    return 'utf-8'
            except UnicodeDecodeError:
                print(f"    ❌ UTF-8解码失败")

        # 泰语字符的字节范围检测
        thai_encodings = ['cp874', 'iso-8859-11', 'tis-620']

        for encoding in thai_encodings:
            try:
                decoded_text = raw_data.decode(encoding)

                # 检查是否包含泰语字符
                thai_char_count = 0
                for char in decoded_text:
                    # 泰语Unicode范围: U+0E00-U+0E7F
                    if '\u0E00' <= char <= '\u0E7F':
                        thai_char_count += 1

                # 如果泰语字符占比超过3%，认为是泰语文本
                if len(decoded_text) > 0 and thai_char_count / len(decoded_text) > 0.03:
                    print(f"    ✅ 检测到泰语编码: {encoding}")
                    return encoding

            except (UnicodeDecodeError, UnicodeError):
                continue

        return None

    def _has_thai_utf8_pattern(self, raw_data: bytes) -> bool:
        """
        检查是否包含泰语UTF-8字节模式

        Args:
            raw_data: 原始字节数据

        Returns:
            bool: 是否包含泰语UTF-8模式
        """
        # 泰语UTF-8字节模式: 0xE0 0xB8-0xBF 0x80-0xBF
        i = 0
        while i < len(raw_data) - 2:
            if (raw_data[i] == 0xE0 and
                0xB8 <= raw_data[i+1] <= 0xBF and
                0x80 <= raw_data[i+2] <= 0xBF):
                return True
            i += 1
        return False

    def _test_encoding_with_hint(self, raw_data: bytes, hint_encoding: str) -> str:
        """
        结合检测提示进行编码测试

        Args:
            raw_data: 原始字节数据
            hint_encoding: 检测提示的编码

        Returns:
            str: 最佳编码
        """
        # 优先测试提示的编码及其相关编码
        priority_encodings = [hint_encoding]

        # 根据提示编码添加相关编码
        if 'utf' in hint_encoding.lower():
            priority_encodings.extend(['utf-8', 'utf-8-sig'])
        elif 'gb' in hint_encoding.lower() or 'chinese' in hint_encoding.lower():
            priority_encodings.extend(['gbk', 'gb2312'])
        elif 'big5' in hint_encoding.lower():
            priority_encodings.extend(['big5'])
        elif 'iso-8859-11' in hint_encoding.lower() or 'cp874' in hint_encoding.lower():
            priority_encodings.extend(['cp874', 'iso-8859-11', 'tis-620'])

        # 添加常用编码作为备选
        priority_encodings.extend(['utf-8', 'latin1', 'cp1252'])

        # 去重并保持顺序
        seen = set()
        unique_encodings = []
        for enc in priority_encodings:
            if enc not in seen:
                seen.add(enc)
                unique_encodings.append(enc)

        best_encoding = 'utf-8'
        best_score = 0

        for encoding in unique_encodings:
            try:
                decoded_text = raw_data.decode(encoding)
                score = self._calculate_text_quality_score(decoded_text)

                print(f"    🔍 测试编码 {encoding}: 分数 {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_encoding = encoding

                if score > 0.9:
                    break

            except (UnicodeDecodeError, UnicodeError):
                continue

        print(f"  ✅ 选择编码: {best_encoding} (分数: {best_score:.2f})")
        return best_encoding

    def _detect_thai_encoding_special(self, raw_data: bytes) -> str:
        """
        专门检测泰语编码问题，包括被错误编码的泰语

        Args:
            raw_data: 原始字节数据

        Returns:
            str: 检测到的泰语编码，如果不是泰语则返回None
        """
        print("  🇹🇭 专门检测泰语编码...")

        # 泰语UTF-8字节模式
        thai_utf8_patterns = [
            b'\xe0\xb8',  # 泰语字符 U+0E00-U+0E3F
            b'\xe0\xb9',  # 泰语字符 U+0E40-U+0E7F
        ]

        # 检查是否包含泰语UTF-8模式
        has_thai_utf8 = any(pattern in raw_data for pattern in thai_utf8_patterns)

        if has_thai_utf8:
            print("    🔍 检测到泰语UTF-8字节模式")
            try:
                decoded = raw_data.decode('utf-8')
                if any('\u0e00' <= char <= '\u0e7f' for char in decoded):
                    print("    ✅ 确认为正确的泰语UTF-8编码")
                    return 'utf-8'
            except UnicodeDecodeError:
                print("    ❌ UTF-8解码失败")

        # 检查被错误编码的泰语（常见问题）
        corrupted_patterns = [
            # UTF-8泰语被错误解析为latin1的模式
            b'\xc3\xa0\xc2\xb8',  # à¸ 模式
            b'\xc3\xa0\xc2\xb9',  # à¹ 模式
            # 其他可能的乱码模式
            b'\xc3\xa0\xc2\xb8\xc2\x81',  # à¸ 模式
            b'\xc3\xa0\xc2\xb8\xc2\x84',  # à¸ 模式
        ]

        for pattern in corrupted_patterns:
            if pattern in raw_data:
                print(f"    🔍 检测到泰语乱码模式: {pattern.hex()}")

                # 尝试修复：假设原始是UTF-8，被错误解析为latin1
                try:
                    # 方法1：latin1解码 -> utf-8编码 -> utf-8解码
                    temp_str = raw_data.decode('latin1')
                    fixed_bytes = temp_str.encode('latin1')
                    fixed_str = fixed_bytes.decode('utf-8')

                    if any('\u0e00' <= char <= '\u0e7f' for char in fixed_str):
                        print("    ✅ 成功修复泰语编码（方法1）")
                        return 'utf-8-corrupted-latin1'
                except:
                    pass

                # 方法2：尝试windows-1252解码修复
                try:
                    temp_str = raw_data.decode('windows-1252')
                    fixed_bytes = temp_str.encode('windows-1252')
                    fixed_str = fixed_bytes.decode('utf-8')

                    if any('\u0e00' <= char <= '\u0e7f' for char in fixed_str):
                        print("    ✅ 成功修复泰语编码（方法2）")
                        return 'utf-8-corrupted-cp1252'
                except:
                    pass

        # 尝试泰语专用编码
        thai_encodings = ['cp874', 'tis-620', 'iso-8859-11']
        for encoding in thai_encodings:
            try:
                decoded = raw_data.decode(encoding)
                if any('\u0e00' <= char <= '\u0e7f' for char in decoded):
                    print(f"    ✅ 检测到泰语编码: {encoding}")
                    return encoding
            except:
                continue

        return None

    def _test_encoding_with_hint(self, raw_data: bytes, hint_encoding: str) -> str:
        """
        结合chardet提示进行编码测试，优化中等置信度情况

        Args:
            raw_data: 原始字节数据
            hint_encoding: chardet检测到的编码提示

        Returns:
            str: 最佳编码
        """
        # 根据提示编码构建优先测试列表
        priority_encodings = []

        # 根据提示编码添加相关编码
        if hint_encoding:
            hint_lower = hint_encoding.lower()

            # 特殊处理windows-1252编码问题
            if 'windows-1252' in hint_lower:
                # windows-1252经常被误检测，优先尝试相关的更通用编码
                priority_encodings.extend(['latin1', 'cp1252', 'iso-8859-1', 'utf-8'])
                print(f"    🔧 检测到windows-1252，优先尝试相关编码")
            else:
                # 添加提示编码本身
                priority_encodings.append(hint_encoding)

            # 根据提示编码添加相关编码族
            if 'utf' in hint_lower:
                priority_encodings.extend(['utf-8', 'utf-8-sig', 'utf-16'])
            elif 'gb' in hint_lower or 'chinese' in hint_lower:
                priority_encodings.extend(['gbk', 'gb2312', 'gb18030'])
            elif 'big5' in hint_lower:
                priority_encodings.extend(['big5', 'big5hkscs'])
            elif 'iso-8859' in hint_lower:
                # 根据具体的ISO编码添加相关编码
                if '1' in hint_lower:
                    priority_encodings.extend(['latin1', 'iso-8859-1', 'cp1252'])
                elif '11' in hint_lower:
                    priority_encodings.extend(['iso-8859-11', 'cp874', 'tis-620'])
                elif '2' in hint_lower:
                    priority_encodings.extend(['iso-8859-2', 'cp1250'])
                elif '5' in hint_lower:
                    priority_encodings.extend(['iso-8859-5', 'cp1251', 'koi8-r'])
            elif 'cp874' in hint_lower or 'tis' in hint_lower:
                priority_encodings.extend(['cp874', 'iso-8859-11', 'tis-620'])
            elif 'cp1252' in hint_lower and 'windows-1252' not in hint_lower:
                priority_encodings.extend(['cp1252', 'latin1', 'iso-8859-1'])
            elif 'cp1251' in hint_lower:
                priority_encodings.extend(['cp1251', 'iso-8859-5', 'koi8-r'])
            elif 'shift_jis' in hint_lower or 'sjis' in hint_lower:
                priority_encodings.extend(['shift_jis', 'euc-jp', 'iso-2022-jp'])
            elif 'euc-kr' in hint_lower:
                priority_encodings.extend(['euc-kr', 'cp949'])

        # 添加通用备选编码
        fallback_encodings = [
            'utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'gbk', 'big5'
        ]

        # 合并并去重
        all_encodings = []
        seen = set()
        for encoding in priority_encodings + fallback_encodings:
            if encoding and encoding not in seen:
                all_encodings.append(encoding)
                seen.add(encoding)

        # 测试编码
        best_encoding = 'utf-8'
        best_score = 0

        print(f"  🎯 基于提示 '{hint_encoding}' 进行优先测试")

        for encoding in all_encodings:
            # 验证编码是否可用
            if not self._is_encoding_available(encoding):
                print(f"    ⚠️  编码 {encoding} 在当前系统不可用，跳过")
                continue

            try:
                decoded_text = raw_data.decode(encoding)
                score = self._calculate_text_quality_score(decoded_text)

                print(f"    🔍 测试编码 {encoding}: 分数 {score:.2f}")

                if score > best_score:
                    best_score = score
                    best_encoding = encoding

                # 如果分数很高，直接使用
                if score > 0.85:
                    break

            except (UnicodeDecodeError, UnicodeError, LookupError):
                print(f"    ❌ 编码 {encoding} 解码失败")
                continue

        print(f"  ✅ 基于提示选择编码: {best_encoding} (分数: {best_score:.2f})")
        return best_encoding

    def _is_encoding_available(self, encoding: str) -> bool:
        """
        检查编码是否在当前系统可用

        Args:
            encoding: 编码名称

        Returns:
            bool: 编码是否可用
        """
        try:
            import codecs
            codecs.lookup(encoding)
            return True
        except (LookupError, TypeError):
            return False

    def _calculate_text_quality_score(self, text: str) -> float:
        """
        计算文本质量分数，用于判断编码是否正确，优化小语种支持

        Args:
            text: 解码后的文本

        Returns:
            float: 质量分数 (0-1)
        """
        if not text:
            return 0.0

        score = 0.0
        total_chars = len(text)

        # 统计各种字符类型
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        printable_chars = sum(1 for c in text if c.isprintable() or c.isspace())
        control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
        replacement_chars = text.count('\ufffd')  # 替换字符，表示解码错误

        # 扩展的语言字符检测
        latin_chars = sum(1 for c in text if '\u0080' <= c <= '\u024f')  # 拉丁扩展（西班牙语、法语等）
        cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04ff')  # 西里尔字母（俄语等）
        greek_chars = sum(1 for c in text if '\u0370' <= c <= '\u03ff')  # 希腊字母
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06ff')  # 阿拉伯字母
        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05ff')  # 希伯来字母
        thai_chars = sum(1 for c in text if '\u0e00' <= c <= '\u0e7f')  # 泰语字符
        japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff')  # 日语假名
        korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7af')  # 韩语字符

        # 计算各种语言字符的总数
        non_ascii_language_chars = (chinese_chars + latin_chars + cyrillic_chars +
                                  greek_chars + arabic_chars + hebrew_chars +
                                  thai_chars + japanese_chars + korean_chars)

        # 计算分数
        if total_chars > 0:
            # 可打印字符比例（基础分）
            printable_ratio = printable_chars / total_chars
            score += printable_ratio * 0.3

            # 控制字符惩罚
            control_ratio = control_chars / total_chars
            score -= control_ratio * 0.4

            # 替换字符惩罚（严重）
            replacement_ratio = replacement_chars / total_chars
            score -= replacement_ratio * 0.6

            # 语言字符加分（更全面的语言支持）
            language_ratio = non_ascii_language_chars / total_chars
            if language_ratio > 0.05:  # 如果有语言特定字符
                score += language_ratio * 0.4  # 提高语言字符权重

                # 特定语言额外加分
                if chinese_chars > 0:
                    score += min(chinese_chars / total_chars, 0.3) * 0.3  # 提高中文权重
                if thai_chars > 0:  # 泰语特别处理
                    score += min(thai_chars / total_chars, 0.3) * 0.25
                if arabic_chars > 0:  # 阿拉伯语特别处理
                    score += min(arabic_chars / total_chars, 0.3) * 0.2
                if latin_chars > 0:  # 西欧语言（包括西班牙语）
                    score += min(latin_chars / total_chars, 0.3) * 0.15

            # ASCII字符适度加分
            ascii_ratio = ascii_chars / total_chars
            if 0.1 < ascii_ratio < 0.9:  # 适度的ASCII字符
                score += 0.1
            elif ascii_ratio >= 0.9 and non_ascii_language_chars == 0:  # 纯ASCII内容
                score += 0.15

            # 检查是否包含常见的字幕时间戳格式
            if '-->' in text and any(char.isdigit() for char in text):
                score += 0.1

            # 检查是否包含常见的字幕序号
            lines = text.split('\n')
            numbered_lines = sum(1 for line in lines if line.strip().isdigit())
            if numbered_lines > 0:
                score += min(numbered_lines / len(lines), 0.1) * 0.1

            # 检查UTF-8错误解码模式（严重惩罚）
            if self._has_utf8_decode_error_pattern(text):
                score *= 0.2  # 大幅降低分数

            # 检查常见的乱码字符组合
            if self._has_common_mojibake_patterns(text):
                score *= 0.3  # 降低乱码文本分数

        return max(0.0, min(1.0, score))

    def _has_utf8_decode_error_pattern(self, text: str) -> bool:
        """
        检查是否包含UTF-8被错误解码的模式

        Args:
            text: 文本内容

        Returns:
            bool: 是否包含错误解码模式
        """
        # 常见的UTF-8中文被错误解码的模式
        utf8_error_patterns = [
            'è¿™',  # "这" 被错误解码
            'æ˜¯',  # "是" 被错误解码
            'æµ‹',  # "测" 被错误解码
            'è¯•',  # "试" 被错误解码
            'æ–‡',  # "文" 被错误解码
            'æœ¬',  # "本" 被错误解码
            'ä¸­',  # "中" 被错误解码
            'å›½',  # "国" 被错误解码
            'äººº',  # "人" 被错误解码
            'å¤§',  # "大" 被错误解码
            'å°',   # "小" 被错误解码
            'æ—¶',  # "时" 被错误解码
            'é—´',  # "间" 被错误解码
        ]

        # 如果包含多个错误解码模式，很可能是编码错误
        error_count = sum(1 for pattern in utf8_error_patterns if pattern in text)
        return error_count >= 2

    def _has_common_mojibake_patterns(self, text: str) -> bool:
        """
        检查是否包含常见的乱码模式

        Args:
            text: 文本内容

        Returns:
            bool: 是否包含乱码模式
        """
        # 常见的乱码字符组合
        mojibake_patterns = [
            'è¿',   # UTF-8中文被latin1解码的常见模式
            'æ˜',   # UTF-8中文被latin1解码的常见模式
            'æµ',   # UTF-8中文被latin1解码的常见模式
            'è¯',   # UTF-8中文被latin1解码的常见模式
            'æ–',   # UTF-8中文被latin1解码的常见模式
            'æœ',   # UTF-8中文被latin1解码的常见模式
            'ä¸',   # UTF-8中文被latin1解码的常见模式
            'å›',   # UTF-8中文被latin1解码的常见模式
            'äº',   # UTF-8中文被latin1解码的常见模式
            'å¤',   # UTF-8中文被latin1解码的常见模式
            'å°',   # UTF-8中文被latin1解码的常见模式
            'æ—',   # UTF-8中文被latin1解码的常见模式
            'é—',   # UTF-8中文被latin1解码的常见模式
        ]

        # 如果包含多个乱码模式，很可能是编码错误
        mojibake_count = sum(1 for pattern in mojibake_patterns if pattern in text)
        return mojibake_count >= 3

    def _read_file_with_encoding_detection(self, file_path: str) -> str:
        """
        使用智能编码检测读取文件，确保不出现乱码

        Args:
            file_path: 文件路径

        Returns:
            str: 文件内容
        """
        print(f"  📖 读取SRT文件: {os.path.basename(file_path)}")

        # 检测文件编码
        self.encoding = self._detect_encoding(file_path)
        print(f"  📝 使用编码: {self.encoding}")

        # 处理特殊的泰语编码修复情况
        if self.encoding.startswith('utf-8-corrupted'):
            return self._read_corrupted_thai_file(file_path, self.encoding)

        # 尝试用检测到的编码读取
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='strict') as f:
                content = f.read()
            print(f"  ✅ 编码 {self.encoding} 读取成功")
            return content
        except UnicodeDecodeError as e:
            print(f"  ⚠️  编码 {self.encoding} 读取失败: {str(e)}")

        # 如果失败，尝试多种编码的容错读取，扩展小语种支持
        fallback_encodings = [
            ('utf-8', 'replace'),
            ('utf-8-sig', 'replace'),

            # 中文编码
            ('gbk', 'replace'),
            ('gb2312', 'replace'),
            ('big5', 'replace'),

            # 西欧语言编码（西班牙语、法语等）
            ('latin1', 'replace'),
            ('cp1252', 'replace'),
            ('iso-8859-1', 'replace'),
            ('iso-8859-15', 'replace'),

            # 泰语编码
            ('cp874', 'replace'),
            ('iso-8859-11', 'replace'),
            ('tis-620', 'replace'),

            # 东欧语言编码
            ('cp1250', 'replace'),
            ('iso-8859-2', 'replace'),

            # 西里尔字母编码（俄语等）
            ('cp1251', 'replace'),
            ('iso-8859-5', 'replace'),
            ('koi8-r', 'replace'),

            # 其他语言编码
            ('cp1253', 'replace'),  # 希腊语
            ('cp1254', 'replace'),  # 土耳其语
            ('cp1255', 'replace'),  # 希伯来语
            ('cp1256', 'replace'),  # 阿拉伯语

            # 日韩语编码
            ('shift_jis', 'replace'),
            ('euc-jp', 'replace'),
            ('euc-kr', 'replace'),
            ('cp949', 'replace'),

            # 最后的备选
            ('ascii', 'ignore'),
            ('cp437', 'replace'),
        ]

        for encoding, error_handling in fallback_encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors=error_handling) as f:
                    content = f.read()

                # 检查内容质量
                quality_score = self._calculate_text_quality_score(content)
                print(f"  🔍 编码 {encoding} (错误处理: {error_handling}) 质量分数: {quality_score:.2f}")

                if quality_score > 0.7:  # 质量足够好
                    self.encoding = encoding
                    print(f"  ✅ 使用编码 {encoding} 读取成功")

                    # 如果使用了错误处理，进行后处理清理
                    if error_handling != 'strict':
                        content = self._clean_decoded_content(content)

                    return content

            except (UnicodeDecodeError, UnicodeError) as e:
                print(f"  ❌ 编码 {encoding} 失败: {str(e)}")
                continue

        # 最后的备用方案：二进制读取并尝试修复
        print(f"  🚨 所有编码都失败，使用二进制读取备用方案")
        return self._binary_fallback_read(file_path)

    def _clean_decoded_content(self, content: str) -> str:
        """
        清理解码后的内容，移除替换字符和其他问题

        Args:
            content: 解码后的内容

        Returns:
            str: 清理后的内容
        """
        # 移除Unicode替换字符
        content = content.replace('\ufffd', '')

        # 移除其他控制字符（保留换行、回车、制表符）
        cleaned_chars = []
        for char in content:
            if char.isprintable() or char in '\n\r\t':
                cleaned_chars.append(char)
            elif ord(char) < 32:
                # 跳过其他控制字符
                continue
            else:
                cleaned_chars.append(char)

        return ''.join(cleaned_chars)

    def _read_corrupted_thai_file(self, file_path: str, encoding_type: str) -> str:
        """
        读取被错误编码的泰语文件并修复

        Args:
            file_path: 文件路径
            encoding_type: 编码类型（包含修复信息）

        Returns:
            str: 修复后的文件内容
        """
        print(f"  🔧 修复泰语编码: {encoding_type}")

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()

            if encoding_type == 'utf-8-corrupted-latin1':
                # 修复方法1：latin1 -> utf-8
                temp_str = raw_data.decode('latin1')
                fixed_bytes = temp_str.encode('latin1')
                content = fixed_bytes.decode('utf-8')
                print("  ✅ 泰语编码修复成功（latin1方法）")

            elif encoding_type == 'utf-8-corrupted-cp1252':
                # 修复方法2：windows-1252 -> utf-8
                temp_str = raw_data.decode('windows-1252')
                fixed_bytes = temp_str.encode('windows-1252')
                content = fixed_bytes.decode('utf-8')
                print("  ✅ 泰语编码修复成功（cp1252方法）")

            else:
                # 默认尝试UTF-8
                content = raw_data.decode('utf-8', errors='replace')
                print("  ⚠️  使用默认UTF-8解码")

            # 验证修复结果
            thai_char_count = sum(1 for char in content if '\u0e00' <= char <= '\u0e7f')
            print(f"  📊 修复后泰语字符数量: {thai_char_count}")

            return content

        except Exception as e:
            print(f"  ❌ 泰语编码修复失败: {e}")
            # 回退到普通UTF-8读取
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()

    def _binary_fallback_read(self, file_path: str) -> str:
        """
        二进制读取备用方案，尽最大努力恢复文本

        Args:
            file_path: 文件路径

        Returns:
            str: 恢复的文本内容
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()

            # 尝试多种编码的组合解码
            for encoding in ['utf-8', 'gbk', 'latin1']:
                try:
                    # 使用ignore错误处理，跳过无法解码的字节
                    content = raw_data.decode(encoding, errors='ignore')
                    if content.strip():  # 如果有有效内容
                        print(f"  🔧 二进制备用方案使用编码: {encoding}")
                        self.encoding = encoding
                        return self._clean_decoded_content(content)
                except:
                    continue

            # 最终备用：逐字节处理
            print(f"  🆘 使用逐字节处理备用方案")
            chars = []
            for byte in raw_data:
                if 32 <= byte <= 126:  # ASCII可打印字符
                    chars.append(chr(byte))
                elif byte in [10, 13, 9]:  # 换行、回车、制表符
                    chars.append(chr(byte))
                # 跳过其他字节

            self.encoding = 'ascii-fallback'
            return ''.join(chars)

        except Exception as e:
            print(f"  💥 二进制备用方案也失败: {str(e)}")
            raise ValueError(f"无法读取SRT文件: {file_path}")
    
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
