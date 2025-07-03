"""
Pexels API管理器 - 用于下载热门视频作为背景
"""
import os
import requests
import json
import tempfile
from typing import Dict, List, Optional, Any
from .configManager import AutoMixConfigManager


class PexelsManager:
    """Pexels API管理器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化Pexels管理器
        
        Args:
            api_key: Pexels API密钥，如果为None则从配置中获取
        """
        self.api_key = api_key or AutoMixConfigManager.get_pexels_api_key()
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {
            "Authorization": self.api_key
        }
        self.cache_dir = os.path.join(tempfile.gettempdir(), "pexels_cache")
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_popular_videos(self, per_page: int = 20, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        获取热门视频列表
        
        Args:
            per_page: 每页视频数量 (最大80)
            page: 页码
            
        Returns:
            Dict: API响应数据，包含视频列表
        """
        try:
            url = f"{self.base_url}/popular"
            params = {
                "per_page": min(per_page, 80),
                "page": page
            }
            
            print(f"🌐 请求Pexels热门视频: {url}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取到 {len(data.get('videos', []))} 个热门视频")
                return data
            else:
                print(f"❌ Pexels API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 获取热门视频失败: {str(e)}")
            return None
    
    def search_videos(self, query: str, per_page: int = 20, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            per_page: 每页视频数量
            page: 页码
            
        Returns:
            Dict: API响应数据，包含视频列表
        """
        try:
            url = f"{self.base_url}/search"
            params = {
                "query": query,
                "per_page": min(per_page, 80),
                "page": page
            }
            
            print(f"🔍 搜索Pexels视频: {query}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 搜索到 {len(data.get('videos', []))} 个相关视频")
                return data
            else:
                print(f"❌ Pexels搜索失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 搜索视频失败: {str(e)}")
            return None
    
    def get_best_video_file(self, video_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        从视频数据中选择最佳的视频文件
        
        Args:
            video_data: 视频数据
            
        Returns:
            Dict: 最佳视频文件信息
        """
        video_files = video_data.get('video_files', [])
        if not video_files:
            return None
        
        # 优先选择HD质量的MP4文件
        preferred_qualities = ['hd', 'sd', 'uhd']
        
        for quality in preferred_qualities:
            for file_info in video_files:
                if (file_info.get('quality') == quality and 
                    file_info.get('file_type') == 'video/mp4'):
                    return file_info
        
        # 如果没有找到首选格式，返回第一个MP4文件
        for file_info in video_files:
            if file_info.get('file_type') == 'video/mp4':
                return file_info
        
        # 最后返回第一个文件
        return video_files[0] if video_files else None
    
    def download_video(self, video_url: str, filename: str = None) -> Optional[str]:
        """
        下载视频文件（带重试机制和SSL错误处理）

        Args:
            video_url: 视频下载URL
            filename: 保存的文件名，如果为None则自动生成

        Returns:
            str: 下载的文件路径，失败返回None
        """
        try:
            if not filename:
                filename = f"pexels_video_{hash(video_url) % 1000000}.mp4"

            file_path = os.path.join(self.cache_dir, filename)

            # 如果文件已存在，直接返回
            if os.path.exists(file_path):
                print(f"📁 使用缓存视频: {filename}")
                return file_path

            print(f"⬇️  下载Pexels视频: {filename}")

            # 配置请求会话，处理SSL问题
            session = requests.Session()
            session.verify = True  # 启用SSL验证

            # 设置重试适配器
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=3,  # 总重试次数
                backoff_factor=1,  # 重试间隔
                status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
                allowed_methods=["HEAD", "GET", "OPTIONS"]  # 允许重试的方法
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            # 设置请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'video/mp4,video/*;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            # 尝试下载
            response = session.get(video_url, stream=True, timeout=120, headers=headers)

            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)

                            # 显示下载进度
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                if downloaded_size % (1024 * 1024) == 0:  # 每MB显示一次
                                    print(f"  📊 下载进度: {progress:.1f}% ({downloaded_size/(1024*1024):.1f}MB/{total_size/(1024*1024):.1f}MB)")

                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"✅ 视频下载完成: {filename} ({file_size:.1f}MB)")
                return file_path
            else:
                print(f"❌ 视频下载失败: HTTP {response.status_code}")
                return None

        except requests.exceptions.SSLError as e:
            print(f"❌ SSL连接错误: {str(e)}")
            print("💡 尝试使用备用下载方法...")
            return self._download_video_fallback(video_url, filename)

        except requests.exceptions.ConnectionError as e:
            print(f"❌ 网络连接错误: {str(e)}")
            print("💡 请检查网络连接或稍后重试")
            return None

        except requests.exceptions.Timeout as e:
            print(f"❌ 下载超时: {str(e)}")
            print("💡 网络较慢，建议稍后重试")
            return None

        except Exception as e:
            print(f"❌ 下载视频异常: {str(e)}")
            return None

    def _download_video_fallback(self, video_url: str, filename: str) -> Optional[str]:
        """
        备用下载方法（禁用SSL验证）

        Args:
            video_url: 视频下载URL
            filename: 保存的文件名

        Returns:
            str: 下载的文件路径，失败返回None
        """
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            file_path = os.path.join(self.cache_dir, filename)

            print(f"🔄 尝试备用下载方法（禁用SSL验证）...")

            # 禁用SSL验证的请求
            response = requests.get(
                video_url,
                stream=True,
                timeout=120,
                verify=False,  # 禁用SSL验证
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"✅ 备用方法下载完成: {filename} ({file_size:.1f}MB)")
                return file_path
            else:
                print(f"❌ 备用下载也失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ 备用下载异常: {str(e)}")
            return None

    def get_anti_detection_overlay_video(self, keywords: List[str] = None) -> Optional[str]:
        """
        获取防审核覆盖层视频

        Args:
            keywords: 搜索关键词列表，如果为None则搜索风景视频

        Returns:
            str: 下载的视频文件路径
        """
        try:
            # 默认搜索风景类视频，适合作为覆盖层
            if not keywords:
                keywords = ["landscape", "nature", "scenery", "mountains", "ocean", "forest", "sunset", "clouds"]

            # 随机选择一个关键词进行搜索
            import random
            keyword = random.choice(keywords)
            print(f"🔍 搜索关键词: {keyword}")
            video_data = self.search_videos(keyword, per_page=10)
            
            if not video_data or not video_data.get('videos'):
                print("❌ 未获取到视频数据")
                return None
            
            # 随机选择一个视频
            import random
            videos = video_data['videos']
            selected_video = random.choice(videos)
            
            print(f"🎬 选择视频: {selected_video.get('id')} - 时长: {selected_video.get('duration', 0)}秒")
            
            # 获取最佳视频文件
            best_file = self.get_best_video_file(selected_video)
            if not best_file:
                print("❌ 未找到合适的视频文件")
                return None
            
            # 下载视频
            video_url = best_file['link']
            filename = f"overlay_video_{selected_video['id']}.mp4"

            return self.download_video(video_url, filename)
            
        except Exception as e:
            print(f"❌ 获取背景视频失败: {str(e)}")
            return None
    
    def test_api_key(self) -> bool:
        """
        测试API密钥是否有效
        
        Returns:
            bool: API密钥是否有效
        """
        try:
            url = f"{self.base_url}/popular"
            params = {"per_page": 1}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                print("✅ Pexels API密钥验证成功")
                return True
            elif response.status_code == 401:
                print("❌ Pexels API密钥无效")
                return False
            else:
                print(f"⚠️  Pexels API响应异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API密钥测试失败: {str(e)}")
            return False
    
    def clear_cache(self):
        """清理缓存目录"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                self._ensure_cache_dir()
                print("✅ Pexels缓存已清理")
        except Exception as e:
            print(f"❌ 清理缓存失败: {str(e)}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            if not os.path.exists(self.cache_dir):
                return {"file_count": 0, "total_size": 0}
            
            file_count = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    file_count += 1
                    total_size += os.path.getsize(file_path)
            
            return {
                "file_count": file_count,
                "total_size": total_size,
                "total_size_mb": total_size / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"❌ 获取缓存信息失败: {str(e)}")
            return {"file_count": 0, "total_size": 0}
