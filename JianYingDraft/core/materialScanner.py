"""
 * @file   : materialScanner.py
 * @time   : 16:10
 * @date   : 2024/12/19
 * @mail   : 9727005@qq.com
 * @creator: ShanDong Xiedali
 * @company: HiLand & RainyTop
"""
import os
import random
from typing import List, Dict, Optional, Tuple, Any
try:
    from pymediainfo import MediaInfo
except ImportError:
    MediaInfo = None
from JianYingDraft.core.mediaFactory import MediaFactory


class MaterialScanner:
    """
    素材库扫描器
    支持递归扫描指定目录，自动识别和分类视频、音频、字幕文件
    """
    
    # 支持的文件格式
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ts'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma', '.m4a', '.opus'}
    SUBTITLE_EXTENSIONS = {'.srt', '.ass', '.ssa', '.vtt', '.sub', '.idx'}
    
    def __init__(self):
        """初始化素材扫描器"""
        self.videos: List[Dict] = []
        self.audios: List[Dict] = []
        self.subtitles: List[Dict] = []
        self.scan_stats = {
            'total_files': 0,
            'video_count': 0,
            'audio_count': 0,
            'subtitle_count': 0,
            'error_count': 0
        }
    
    def scan_directory(self, directory_path: str, progress_callback=None) -> bool:
        """
        递归扫描指定目录
        
        Args:
            directory_path: 要扫描的目录路径
            progress_callback: 进度回调函数
            
        Returns:
            bool: 扫描是否成功
        """
        if not os.path.exists(directory_path):
            print(f"错误：目录不存在 - {directory_path}")
            return False
        
        if not os.path.isdir(directory_path):
            print(f"错误：路径不是目录 - {directory_path}")
            return False
        
        print(f"开始扫描目录: {directory_path}")
        
        # 重置统计信息
        self._reset_stats()
        
        try:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.scan_stats['total_files'] += 1
                    
                    try:
                        self._process_file(file_path)
                        
                        # 调用进度回调
                        if progress_callback:
                            progress_callback(self.scan_stats['total_files'], file_path)
                            
                    except Exception as e:
                        print(f"处理文件时出错 {file_path}: {str(e)}")
                        self.scan_stats['error_count'] += 1
                        continue
            
            self._print_scan_summary()
            return True
            
        except Exception as e:
            print(f"扫描目录时出错: {str(e)}")
            return False
    
    def _reset_stats(self):
        """重置统计信息"""
        self.videos.clear()
        self.audios.clear()
        self.subtitles.clear()
        self.scan_stats = {
            'total_files': 0,
            'video_count': 0,
            'audio_count': 0,
            'subtitle_count': 0,
            'error_count': 0
        }
    
    def _process_file(self, file_path: str):
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in self.VIDEO_EXTENSIONS:
            self._process_video_file(file_path)
        elif file_ext in self.AUDIO_EXTENSIONS:
            self._process_audio_file(file_path)
        elif file_ext in self.SUBTITLE_EXTENSIONS:
            self._process_subtitle_file(file_path)
    
    def _process_video_file(self, file_path: str):
        """处理视频文件"""
        try:
            # 使用MediaFactory检测文件信息
            media_info = MediaInfo.parse(file_path).to_data()["tracks"]
            
            # 查找视频轨道
            video_track = None
            for track in media_info:
                if track.get('track_type') == 'Video':
                    video_track = track
                    break
            
            if video_track:
                video_info = {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size': os.path.getsize(file_path),
                    'duration': int(float(video_track.get('duration', 0)) * 1000),  # 转换为微秒
                    'width': video_track.get('width', 0),
                    'height': video_track.get('height', 0),
                    'frame_rate': video_track.get('frame_rate', 0),
                    'format': video_track.get('format', ''),
                    'codec': video_track.get('codec_id', ''),
                    'bit_rate': video_track.get('bit_rate', 0)
                }
                
                self.videos.append(video_info)
                self.scan_stats['video_count'] += 1
                
        except Exception as e:
            print(f"处理视频文件失败 {file_path}: {str(e)}")
            raise
    
    def _process_audio_file(self, file_path: str):
        """处理音频文件"""
        try:
            media_info = MediaInfo.parse(file_path).to_data()["tracks"]
            
            # 查找音频轨道
            audio_track = None
            for track in media_info:
                if track.get('track_type') == 'Audio':
                    audio_track = track
                    break
            
            if audio_track:
                audio_info = {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size': os.path.getsize(file_path),
                    'duration': int(float(audio_track.get('duration', 0)) * 1000),  # 转换为微秒
                    'sample_rate': audio_track.get('sampling_rate', 0),
                    'channels': audio_track.get('channel_s', 0),
                    'format': audio_track.get('format', ''),
                    'codec': audio_track.get('codec_id', ''),
                    'bit_rate': audio_track.get('bit_rate', 0)
                }
                
                self.audios.append(audio_info)
                self.scan_stats['audio_count'] += 1
                
        except Exception as e:
            print(f"处理音频文件失败 {file_path}: {str(e)}")
            raise
    
    def _process_subtitle_file(self, file_path: str):
        """处理字幕文件"""
        try:
            subtitle_info = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'format': os.path.splitext(file_path)[1].lower(),
                'encoding': self._detect_encoding(file_path)
            }
            
            self.subtitles.append(subtitle_info)
            self.scan_stats['subtitle_count'] += 1
            
        except Exception as e:
            print(f"处理字幕文件失败 {file_path}: {str(e)}")
            raise
    
    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10KB
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'
    
    def _print_scan_summary(self):
        """打印扫描摘要"""
        print("\n=== 扫描完成 ===")
        print(f"总文件数: {self.scan_stats['total_files']}")
        print(f"视频文件: {self.scan_stats['video_count']}")
        print(f"音频文件: {self.scan_stats['audio_count']}")
        print(f"字幕文件: {self.scan_stats['subtitle_count']}")
        print(f"错误文件: {self.scan_stats['error_count']}")
        print("==================")
    
    def get_random_videos(self, count: int, min_duration: int = 0, max_duration: int = None) -> List[Dict]:
        """
        随机选择指定数量的视频文件
        
        Args:
            count: 要选择的视频数量
            min_duration: 最小时长（微秒）
            max_duration: 最大时长（微秒）
            
        Returns:
            List[Dict]: 随机选择的视频信息列表
        """
        filtered_videos = self.filter_videos_by_duration(min_duration, max_duration)
        
        if len(filtered_videos) < count:
            print(f"警告：可用视频数量({len(filtered_videos)})少于请求数量({count})")
            return filtered_videos
        
        return random.sample(filtered_videos, count)
    
    def get_random_audios(self, count: int, min_duration: int = 0, max_duration: int = None) -> List[Dict]:
        """随机选择指定数量的音频文件"""
        filtered_audios = self.filter_audios_by_duration(min_duration, max_duration)
        
        if len(filtered_audios) < count:
            print(f"警告：可用音频数量({len(filtered_audios)})少于请求数量({count})")
            return filtered_audios
        
        return random.sample(filtered_audios, count)
    
    def get_random_subtitles(self, count: int) -> List[Dict]:
        """随机选择指定数量的字幕文件"""
        if len(self.subtitles) < count:
            print(f"警告：可用字幕数量({len(self.subtitles)})少于请求数量({count})")
            return self.subtitles
        
        return random.sample(self.subtitles, count)
    
    def filter_videos_by_duration(self, min_duration: int = 0, max_duration: int = None) -> List[Dict]:
        """根据时长过滤视频文件"""
        filtered = []
        for video in self.videos:
            duration = video.get('duration', 0)
            if duration >= min_duration:
                if max_duration is None or duration <= max_duration:
                    filtered.append(video)
        return filtered
    
    def filter_audios_by_duration(self, min_duration: int = 0, max_duration: int = None) -> List[Dict]:
        """根据时长过滤音频文件"""
        filtered = []
        for audio in self.audios:
            duration = audio.get('duration', 0)
            if duration >= min_duration:
                if max_duration is None or duration <= max_duration:
                    filtered.append(audio)
        return filtered
    
    def get_scan_stats(self) -> Dict:
        """获取扫描统计信息"""
        return self.scan_stats.copy()

    def _get_subtitle_info(self, file_path: str) -> Optional[Dict]:
        """获取字幕文件信息"""
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)

            # 检测编码
            encoding = self._detect_encoding(file_path)

            return {
                'path': file_path,
                'filename': filename,
                'size': file_size,
                'encoding': encoding,
                'type': 'subtitle'
            }
        except Exception as e:
            print(f"获取字幕信息失败 {file_path}: {str(e)}")
            return None

    def _get_audio_info(self, file_path: str) -> Optional[Dict]:
        """获取音频文件信息"""
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)

            # 尝试使用MediaInfo获取详细信息
            duration = 0
            if MediaInfo:
                try:
                    media_info = MediaInfo.parse(file_path)
                    for track in media_info.tracks:
                        if track.track_type == 'Audio':
                            duration = int(float(track.duration or 0) * 1000)  # 转换为微秒
                            break
                except Exception:
                    pass

            return {
                'path': file_path,
                'filename': filename,
                'size': file_size,
                'duration': duration,
                'type': 'audio'
            }
        except Exception as e:
            print(f"获取音频信息失败 {file_path}: {str(e)}")
            return None

    def _get_video_info(self, file_path: str) -> Optional[Dict]:
        """获取视频文件信息"""
        try:
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)

            # 尝试使用MediaInfo获取详细信息
            duration = 0
            width = 0
            height = 0

            if MediaInfo:
                try:
                    media_info = MediaInfo.parse(file_path)
                    for track in media_info.tracks:
                        if track.track_type == 'Video':
                            duration = int(float(track.duration or 0) * 1000)  # 转换为微秒
                            width = track.width or 0
                            height = track.height or 0
                            break
                except Exception:
                    pass

            # 计算去掉前3秒后的可用时长
            trim_duration = 3000000  # 3秒
            available_duration = max(0, duration - trim_duration)

            return {
                'path': file_path,
                'filename': filename,
                'size': file_size,
                'duration': duration,
                'available_duration': available_duration,
                'width': width,
                'height': height,
                'type': 'video'
            }
        except Exception as e:
            print(f"获取视频信息失败 {file_path}: {str(e)}")
            return None
    
    def get_all_materials(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """获取所有扫描到的素材"""
        return self.videos.copy(), self.audios.copy(), self.subtitles.copy()

    def scan_product_materials(self, base_path: str, product_model: str = None) -> Dict[str, Any]:
        """
        扫描指定产品型号的素材

        Args:
            base_path: 素材库基础路径
            product_model: 产品型号（如A83），如果为None则随机选择

        Returns:
            Dict[str, Any]: 扫描结果
        """
        try:
            # 如果没有指定产品型号，随机选择一个
            if product_model is None:
                product_model = self._select_random_product(base_path)

            product_path = os.path.join(base_path, product_model)
            if not os.path.exists(product_path):
                raise ValueError(f"产品型号目录不存在: {product_path}")

            print(f"扫描产品型号: {product_model}")
            print(f"产品路径: {product_path}")

            # 扫描产品目录下的所有文件夹
            product_materials = {
                'product_model': product_model,
                'product_path': product_path,
                'folders': [],
                'videos': [],
                'audios': [],
                'subtitles': [],
                'background_audios': []
            }

            # 扫描每个子文件夹
            for item in os.listdir(product_path):
                folder_path = os.path.join(product_path, item)
                if os.path.isdir(folder_path):
                    folder_materials = self._scan_folder_materials(folder_path, item)
                    product_materials['folders'].append(folder_materials)

                    # 合并到总列表
                    product_materials['videos'].extend(folder_materials['videos'])
                    product_materials['audios'].extend(folder_materials['audios'])
                    product_materials['subtitles'].extend(folder_materials['subtitles'])

            # 扫描环境音效（在素材库同级的音效目录）
            background_audio_path = os.path.join(base_path, "音效")
            if os.path.exists(background_audio_path):
                background_audios = self._scan_background_audios(background_audio_path)
                product_materials['background_audios'] = background_audios
            else:
                print(f"环境音效目录不存在: {background_audio_path}")
                product_materials['background_audios'] = []

            print(f"扫描完成: {len(product_materials['folders'])}个文件夹, "
                  f"{len(product_materials['videos'])}个视频, "
                  f"{len(product_materials['audios'])}个音频, "
                  f"{len(product_materials['subtitles'])}个字幕, "
                  f"{len(product_materials['background_audios'])}个环境音效")

            return product_materials

        except Exception as e:
            print(f"扫描产品素材失败: {str(e)}")
            return {
                'product_model': product_model or 'Unknown',
                'product_path': '',
                'folders': [],
                'videos': [],
                'audios': [],
                'subtitles': [],
                'background_audios': []
            }

    def _select_random_product(self, base_path: str) -> str:
        """随机选择一个产品型号"""
        try:
            if not os.path.exists(base_path):
                raise ValueError(f"素材库路径不存在: {base_path}")

            # 获取所有子目录作为产品型号
            products = [item for item in os.listdir(base_path)
                       if os.path.isdir(os.path.join(base_path, item))]

            if not products:
                raise ValueError("素材库中没有找到产品型号目录")

            # 随机选择一个产品型号
            selected_product = random.choice(products)
            print(f"随机选择产品型号: {selected_product}")
            return selected_product

        except Exception as e:
            print(f"选择产品型号失败: {str(e)}")
            return "A83"  # 默认产品型号

    def _scan_folder_materials(self, folder_path: str, folder_name: str) -> Dict[str, Any]:
        """扫描单个文件夹的素材"""
        folder_materials = {
            'folder_name': folder_name,
            'folder_path': folder_path,
            'videos': [],
            'audios': [],
            'subtitles': []
        }

        try:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file_name)[1].lower()

                    if file_ext in self.VIDEO_EXTENSIONS:
                        video_info = self._get_video_info(file_path)
                        if video_info:
                            video_info['folder_name'] = folder_name
                            folder_materials['videos'].append(video_info)

                    elif file_ext in self.AUDIO_EXTENSIONS:
                        audio_info = self._get_audio_info(file_path)
                        if audio_info:
                            audio_info['folder_name'] = folder_name
                            folder_materials['audios'].append(audio_info)

                    elif file_ext in self.SUBTITLE_EXTENSIONS:
                        subtitle_info = self._get_subtitle_info(file_path)
                        if subtitle_info:
                            subtitle_info['folder_name'] = folder_name
                            folder_materials['subtitles'].append(subtitle_info)

        except Exception as e:
            print(f"扫描文件夹失败 {folder_path}: {str(e)}")

        return folder_materials

    def _scan_background_audios(self, audio_path: str) -> List[Dict]:
        """扫描环境音效"""
        background_audios = []

        try:
            for file_name in os.listdir(audio_path):
                file_path = os.path.join(audio_path, file_name)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file_name)[1].lower()

                    if file_ext in self.AUDIO_EXTENSIONS:
                        audio_info = self._get_audio_info(file_path)
                        if audio_info:
                            audio_info['audio_type'] = 'background'
                            background_audios.append(audio_info)

        except Exception as e:
            print(f"扫描环境音效失败 {audio_path}: {str(e)}")

        return background_audios

    def select_materials_from_product(self, product_materials: Dict[str, Any],
                                    video_count: int = 4) -> Dict[str, Any]:
        """
        从产品素材中智能选择素材

        Args:
            product_materials: 产品素材数据
            video_count: 需要的视频数量

        Returns:
            Dict[str, Any]: 选择的素材
        """
        selected_materials = {
            'videos': [],
            'narration_audio': None,
            'background_audio': None,
            'subtitle_file': None,
            'product_model': product_materials['product_model']
        }

        try:
            # 1. 选择视频素材（从不同文件夹中选择）
            available_videos = product_materials['videos']
            if available_videos:
                # 按文件夹分组
                videos_by_folder = {}
                for video in available_videos:
                    folder = video.get('folder_name', 'unknown')
                    if folder not in videos_by_folder:
                        videos_by_folder[folder] = []
                    videos_by_folder[folder].append(video)

                # 确保从每个文件夹都选择至少一个视频
                selected_videos = []
                folders = list(videos_by_folder.keys())

                print(f"发现 {len(folders)} 个子文件夹: {folders}")

                # 第一轮：从每个文件夹选择一个视频
                for folder in folders:
                    if videos_by_folder[folder]:
                        video = random.choice(videos_by_folder[folder])
                        selected_videos.append(video)
                        videos_by_folder[folder].remove(video)
                        print(f"  从文件夹 '{folder}' 选择视频: {video['filename']}")

                # 第二轮：如果还需要更多视频，继续从有视频的文件夹选择
                remaining_count = video_count - len(selected_videos)
                available_folders = [f for f in folders if videos_by_folder[f]]

                for i in range(remaining_count):
                    if not available_folders:
                        break

                    folder = available_folders[i % len(available_folders)]
                    if videos_by_folder[folder]:
                        video = random.choice(videos_by_folder[folder])
                        selected_videos.append(video)
                        videos_by_folder[folder].remove(video)
                        print(f"  额外从文件夹 '{folder}' 选择视频: {video['filename']}")

                        # 如果文件夹空了，移除它
                        if not videos_by_folder[folder]:
                            available_folders.remove(folder)

                selected_materials['videos'] = selected_videos

            # 2. 选择解说音频（优先选择有音频的文件夹）
            available_audios = product_materials['audios']
            if available_audios:
                # 优先选择与已选视频同文件夹的音频
                selected_folders = {v.get('folder_name') for v in selected_materials['videos']}

                folder_audios = [a for a in available_audios
                               if a.get('folder_name') in selected_folders]

                if folder_audios:
                    selected_materials['narration_audio'] = random.choice(folder_audios)['path']
                else:
                    selected_materials['narration_audio'] = random.choice(available_audios)['path']

            # 3. 选择背景音效
            background_audios = product_materials['background_audios']
            if background_audios:
                selected_materials['background_audio'] = random.choice(background_audios)['path']

            # 4. 选择字幕文件
            available_subtitles = product_materials['subtitles']
            if available_subtitles:
                # 优先选择与已选视频同文件夹的字幕
                selected_folders = {v.get('folder_name') for v in selected_materials['videos']}

                folder_subtitles = [s for s in available_subtitles
                                  if s.get('folder_name') in selected_folders]

                if folder_subtitles:
                    selected_materials['subtitle_file'] = random.choice(folder_subtitles)['path']
                else:
                    selected_materials['subtitle_file'] = random.choice(available_subtitles)['path']

            print(f"素材选择完成:")
            print(f"  视频: {len(selected_materials['videos'])}个")
            print(f"  解说音频: {'有' if selected_materials['narration_audio'] else '无'}")
            print(f"  背景音效: {'有' if selected_materials['background_audio'] else '无'}")
            print(f"  字幕文件: {'有' if selected_materials['subtitle_file'] else '无'}")

            return selected_materials

        except Exception as e:
            print(f"选择素材失败: {str(e)}")
            return selected_materials
