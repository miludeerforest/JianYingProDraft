"""
转场媒体类
* @author: HiLand & RainyTop
* @company: HiLand & RainyTop
"""

from JianYingDraft.core.media import Media
from JianYingDraft.core import template
from JianYingDraft.utils import tools


class MediaTransition(Media):

    def __init__(self, **kwargs):
        kwargs.setdefault("media_type", "transition")
        super().__init__(**kwargs)

    def _set_material_data_for_content(self):
        """
        设置草稿文件的content部分
        """
        transition_name_or_resource_id = self.kwargs.get("transition_name_or_resource_id")

        transition_data = tools.generate_transition_data(
            transition_name_or_resource_id, 
            duration=self.duration
        )
        transition_data.guid = self.id

        transition_entity = template.get_transition(
            transition_data.guid, 
            transition_data.resource_id, 
            transition_data.name,
            transition_data.duration
        )

        self.material_data_for_content["transitions"] = transition_entity

        # 转场的各种业务信息为空。后续供track下的segment使用
        self.material_data_for_content["X.extra_material_refs"] = []

    pass
