"""
自动混剪功能测试用例
"""
import unittest
import os
import sys
import tempfile
import shutil
import time
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from JianYingDraft.core.autoMixDraft import AutoMixDraft
from JianYingDraft.core.materialScanner import MaterialScanner
from JianYingDraft.core.metadataManager import MetadataManager
from JianYingDraft.core.randomEffectEngine import RandomEffectEngine
from JianYingDraft.core.videoProcessor import VideoProcessor
from JianYingDraft.core.dualAudioManager import DualAudioManager
from JianYingDraft.core.srtProcessor import SRTProcessor
from JianYingDraft.core.durationController import DurationController
from JianYingDraft.core.configManager import AutoMixConfigManager


class TestAutoMix(unittest.TestCase):
    """自动混剪功能测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.test_dir = tempfile.mkdtemp()
        cls.test_resources_dir = os.path.join(os.path.dirname(__file__), '_res')
        
        # 创建测试视频文件
        cls.test_videos = []
        for i in range(5):
            video_path = os.path.join(cls.test_dir, f'test_video_{i+1}.mp4')
            with open(video_path, 'wb') as f:
                f.write(b'fake video content')
            cls.test_videos.append(video_path)
        
        # 创建测试音频文件
        cls.test_audio = os.path.join(cls.test_dir, 'test_audio.mp3')
        with open(cls.test_audio, 'wb') as f:
            f.write(b'fake audio content')
        
        # 创建测试SRT文件
        cls.test_srt = os.path.join(cls.test_dir, 'test_subtitle.srt')
        with open(cls.test_srt, 'w', encoding='utf-8') as f:
            f.write("""1
00:00:01,000 --> 00:00:03,500
测试字幕1

2
00:00:04,000 --> 00:00:07,200
测试字幕2

3
00:00:08,000 --> 00:00:10,500
测试字幕3
""")
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """每个测试方法的初始化"""
        self.auto_draft = AutoMixDraft("TestDraft")
    
    def test_material_scanning(self):
        """测试素材扫描功能"""
        scanner = MaterialScanner()
        
        # 测试扫描目录
        success = scanner.scan_directory(self.test_dir)
        self.assertTrue(success, "素材扫描应该成功")
        
        # 测试文件识别
        videos, audios, subtitles = scanner.get_all_materials()
        self.assertEqual(len(videos), 0, "应该识别出0个视频文件（测试文件不是真实视频）")
        self.assertEqual(len(audios), 0, "应该识别出0个音频文件")
        self.assertEqual(len(subtitles), 1, "应该识别出1个字幕文件")

        # 测试过滤功能
        filtered_videos = scanner.filter_videos_by_duration(0, None)
        self.assertIsInstance(filtered_videos, list, "过滤结果应该是列表")
    
    def test_metadata_management(self):
        """测试元数据管理"""
        metadata_manager = MetadataManager()
        
        # 测试滤镜加载
        filters = metadata_manager.get_available_filters()
        self.assertGreater(len(filters), 0, "应该加载滤镜元数据")
        
        # 测试转场加载
        transitions = metadata_manager.get_available_transitions()
        self.assertGreater(len(transitions), 0, "应该加载转场元数据")
        
        # 测试特效加载
        effects = metadata_manager.get_available_effects()
        self.assertGreater(len(effects), 0, "应该加载特效元数据")
        
        # 测试VIP过滤
        free_filters = metadata_manager.get_available_filters(free_only=True)
        vip_filters = metadata_manager.get_available_filters(vip_only=True)
        self.assertGreater(len(free_filters), 0, "应该有免费滤镜")
        self.assertGreater(len(vip_filters), 0, "应该有VIP滤镜")
        
        # 测试随机选择
        random_filter = metadata_manager.get_random_filter()
        self.assertIsNotNone(random_filter, "应该能随机选择滤镜")
        
        # 测试统计信息
        stats = metadata_manager.get_metadata_stats()
        self.assertIn('filters', stats, "统计信息应该包含滤镜数据")
        self.assertIn('transitions', stats, "统计信息应该包含转场数据")
        self.assertIn('effects', stats, "统计信息应该包含特效数据")
    
    def test_duration_control(self):
        """测试时长控制"""
        controller = DurationController()
        
        # 创建测试素材
        test_materials = [
            {'path': 'test1.mp4', 'duration': 15000000, 'available_duration': 12000000},
            {'path': 'test2.mp4', 'duration': 20000000, 'available_duration': 17000000},
            {'path': 'test3.mp4', 'duration': 10000000, 'available_duration': 7000000},
            {'path': 'test4.mp4', 'duration': 25000000, 'available_duration': 22000000}
        ]
        
        # 测试时长分配
        durations = controller.calculate_segment_durations(test_materials, 35000000)
        self.assertEqual(len(durations), 4, "应该为4个素材分配时长")
        
        # 测试总时长控制
        result = controller.optimize_duration_distribution(test_materials, 35000000)
        self.assertTrue(result['success'], "时长优化应该成功")
        
        total_duration = result['total_duration']
        min_duration, max_duration = controller.config_manager.get_video_duration_range()
        self.assertGreaterEqual(total_duration, min_duration, "总时长应该不小于最小值")
        self.assertLessEqual(total_duration, max_duration, "总时长应该不大于最大值")
        
        # 测试验证功能
        is_valid, message = controller.validate_total_duration(
            result['segment_durations'], 
            result['transition_durations']
        )
        self.assertTrue(is_valid, f"时长验证应该通过: {message}")
    
    def test_effect_application(self):
        """测试特效应用"""
        metadata_manager = MetadataManager()
        effect_engine = RandomEffectEngine(metadata_manager)
        
        test_segment = {'duration': 5000000, 'start_time': 0}
        
        # 测试滤镜选择
        for _ in range(10):  # 多次测试以验证随机性
            selected_filter = effect_engine.select_filter_for_segment(test_segment)
            if selected_filter:
                self.assertTrue(hasattr(selected_filter, 'name'), "滤镜应该有名称属性")
                break
        
        # 测试特效选择
        for _ in range(10):
            selected_effect = effect_engine.select_effect_for_segment(test_segment)
            if selected_effect:
                self.assertTrue(hasattr(selected_effect, 'name'), "特效应该有名称属性")
                break
        
        # 测试转场选择
        prev_segment = test_segment.copy()
        next_segment = test_segment.copy()
        next_segment['start_time'] = 5000000
        
        for _ in range(10):
            transition_result = effect_engine.select_transition_between_segments(prev_segment, next_segment)
            if transition_result:
                transition_meta, duration = transition_result
                self.assertTrue(hasattr(transition_meta, 'name'), "转场应该有名称属性")
                self.assertGreater(duration, 0, "转场时长应该大于0")
                break
        
        # 测试参数生成
        available_effects = metadata_manager.get_available_effects()
        effects_with_params = [e for e in available_effects if getattr(e, 'params', [])]
        
        if effects_with_params:
            test_effect = effects_with_params[0]
            random_params = effect_engine.generate_random_parameters(test_effect)
            self.assertIsInstance(random_params, list, "参数应该是列表")
            
            for param in random_params:
                self.assertGreaterEqual(param, 0, "参数值应该不小于0")
                self.assertLessEqual(param, 100, "参数值应该不大于100")
    
    def test_audio_processing(self):
        """测试音频处理"""
        audio_manager = DualAudioManager()
        
        # 测试音频轨道创建
        track = audio_manager.create_audio_track()
        self.assertIn('id', track, "音频轨道应该有ID")
        self.assertIn('segments', track, "音频轨道应该有片段列表")
        
        # 测试音频片段创建
        audio_info = {
            'id': 'test_audio_id',
            'path': self.test_audio,
            'duration': 10000000  # 10秒
        }
        
        segment = audio_manager.create_audio_segment(audio_info, 0, 5000000, 1.0)
        self.assertEqual(segment['volume'], 1.0, "音量应该设置正确")
        self.assertEqual(segment['target_timerange']['duration'], 5000000, "时长应该设置正确")
        
        # 测试音量配置
        narration_volume, background_volume = audio_manager.config_manager.get_audio_volumes()
        self.assertEqual(narration_volume, 1.0, "解说音量应该是100%")
        self.assertEqual(background_volume, 0.1, "背景音量应该是10%")
        
        # 测试验证功能
        is_valid, errors = audio_manager.validate_audio_setup()
        self.assertTrue(is_valid or len(errors) == 1, "空音频设置验证应该通过或只有一个错误")
    
    def test_subtitle_processing(self):
        """测试字幕处理"""
        srt_processor = SRTProcessor()
        
        # 测试SRT解析
        subtitles = srt_processor.parse_srt_file(self.test_srt)
        self.assertEqual(len(subtitles), 3, "应该解析出3个字幕")
        
        for subtitle in subtitles:
            self.assertIn('text', subtitle, "字幕应该有文本")
            self.assertIn('start_time', subtitle, "字幕应该有开始时间")
            self.assertIn('end_time', subtitle, "字幕应该有结束时间")
            self.assertIn('duration', subtitle, "字幕应该有时长")
        
        # 测试格式修复
        fixed_subtitles = srt_processor.fix_srt_format(subtitles)
        self.assertLessEqual(len(fixed_subtitles), len(subtitles), "修复后字幕数量应该不增加")
        
        # 测试时长优化
        optimized_subtitles = srt_processor.optimize_subtitle_timing(fixed_subtitles, 30000000)
        for subtitle in optimized_subtitles:
            self.assertLessEqual(subtitle['end_time'], 30000000, "字幕结束时间不应超过视频时长")
        
        # 测试字幕片段创建
        segments = srt_processor.create_subtitle_segments(optimized_subtitles)
        self.assertEqual(len(segments), len(optimized_subtitles), "字幕片段数量应该匹配")
        
        for segment_data in segments:
            self.assertIn('segment', segment_data, "应该包含片段数据")
            self.assertIn('material', segment_data, "应该包含素材数据")
            self.assertIn('subtitle_info', segment_data, "应该包含字幕信息")
    
    def test_video_processing(self):
        """测试视频处理"""
        processor = VideoProcessor()
        
        # 测试视频信息
        test_video_info = {
            'path': self.test_videos[0],
            'filename': 'test_video_1.mp4',
            'duration': 10000000,  # 10秒
            'width': 1920,
            'height': 1080
        }
        
        # 测试去前3秒
        processed_media = processor.trim_start(test_video_info.copy())
        self.assertIn('start_in_media', processed_media, "应该设置开始时间")
        self.assertIn('available_duration', processed_media, "应该计算可用时长")
        
        # 测试画面缩放
        test_segment = {'clip': {'scale': {'x': 1.0, 'y': 1.0}}}
        scaled_segment = processor.scale_video(test_segment.copy())
        scale_factor = processor.config_manager.get_video_scale_factor()
        self.assertEqual(scaled_segment['clip']['scale']['x'], scale_factor, "X缩放应该正确")
        self.assertEqual(scaled_segment['clip']['scale']['y'], scale_factor, "Y缩放应该正确")
        
        # 测试色彩调整
        color_segment = processor.adjust_color_randomly({})
        self.assertTrue(color_segment['enable_color_curves'], "应该启用色彩曲线")
        self.assertTrue(color_segment['enable_color_wheels'], "应该启用色彩轮")
        self.assertIn('_color_adjustments', color_segment, "应该记录色彩调整信息")
        
        # 测试综合处理
        media_info, segment_info = processor.process_video_segment(test_video_info, 5000000)
        self.assertIsNotNone(segment_info, "应该返回片段信息")
        self.assertIn('target_timerange', segment_info, "应该包含目标时间范围")
    
    @patch('JianYingDraft.core.autoMixDraft.AutoMixDraft._scan_materials')
    @patch('JianYingDraft.core.autoMixDraft.AutoMixDraft.add_media')
    @patch('JianYingDraft.core.autoMixDraft.AutoMixDraft.save')
    def test_complete_workflow(self, mock_save, mock_add_media, mock_scan_materials):
        """测试完整工作流程"""
        # 模拟素材扫描结果
        mock_materials = [
            {'path': self.test_videos[0], 'duration': 15000000, 'available_duration': 12000000},
            {'path': self.test_videos[1], 'duration': 20000000, 'available_duration': 17000000},
            {'path': self.test_videos[2], 'duration': 10000000, 'available_duration': 7000000},
            {'path': self.test_videos[3], 'duration': 25000000, 'available_duration': 22000000}
        ]
        mock_scan_materials.return_value = mock_materials
        
        # 模拟添加媒体成功
        mock_add_media.return_value = None
        
        # 模拟保存成功
        mock_save.return_value = None
        
        # 执行自动混剪
        result = self.auto_draft.auto_mix(
            target_duration=35000000,
            narration_audio=self.test_audio,
            background_audio=self.test_audio,
            subtitle_file=self.test_srt
        )
        
        # 验证结果
        self.assertTrue(result['success'], f"自动混剪应该成功: {result.get('error', '')}")
        self.assertIn('draft_path', result, "结果应该包含草稿路径")
        self.assertIn('statistics', result, "结果应该包含统计信息")
        self.assertIn('duration', result, "结果应该包含时长信息")
        
        # 验证统计信息
        stats = result['statistics']
        self.assertEqual(stats['total_materials'], 4, "应该扫描到4个素材")
        self.assertEqual(stats['selected_materials'], 4, "应该选择4个素材")
        
        # 验证方法调用
        mock_scan_materials.assert_called_once()
        self.assertGreater(mock_add_media.call_count, 0, "应该调用添加媒体方法")
        mock_save.assert_called_once()
    
    def test_batch_generation(self):
        """测试批量生成"""
        with patch.object(self.auto_draft, 'auto_mix') as mock_auto_mix:
            # 模拟自动混剪成功
            mock_auto_mix.return_value = {
                'success': True,
                'draft_path': '/test/path',
                'statistics': {},
                'duration': 35000000
            }
            
            # 测试批量生成
            results = self.auto_draft.batch_generate(3, target_duration=35000000)
            
            # 验证结果
            self.assertEqual(len(results), 3, "应该生成3个结果")
            
            for i, result in enumerate(results):
                self.assertTrue(result['success'], f"第{i+1}个结果应该成功")
                self.assertEqual(result['batch_index'], i+1, "批次索引应该正确")
                self.assertIn('draft_name', result, "应该包含草稿名称")
    
    def test_performance(self):
        """测试性能"""
        start_time = time.time()
        
        # 测试初始化性能
        for _ in range(10):
            auto_draft = AutoMixDraft(f"PerfTest_{time.time()}")
            self.assertIsNotNone(auto_draft, "应该能快速初始化")
        
        end_time = time.time()
        init_time = end_time - start_time
        
        # 初始化时间应该在合理范围内（10个实例在5秒内）
        self.assertLess(init_time, 5.0, "初始化性能应该满足要求")
        
        # 测试元数据加载性能
        start_time = time.time()
        metadata_manager = MetadataManager()
        stats = metadata_manager.get_metadata_stats()
        end_time = time.time()
        
        metadata_time = end_time - start_time
        self.assertLess(metadata_time, 2.0, "元数据加载应该在2秒内完成")
        self.assertGreater(stats['filters']['total'], 0, "应该加载滤镜数据")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
