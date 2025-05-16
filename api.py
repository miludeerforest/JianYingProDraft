
import sys
sys.path.append("scripts\JianyingDraft")
from scripts.JianyingDraft.draftContext import DraftContext
from scripts.JianyingDraft.JianYingDraft.utils import tools
from scripts.JianyingDraft.JianYingDraft.utils.dataStruct import TransitionData, AnimationData

def add_media_item(context,data:dict,**kwargs):
    
    duration = data.get("duration",5_00_00)
    #添加转场
    transition_data: TransitionData = tools.generate_transition_data(
        name_or_resource_id=data.get("transition","翻页"),  # 转场名称（可以是内置的转场名称，也可以是剪映本身的转场资源id）
        duration=data.get("transition_duration",0),  # 转场持续时间 
    )

    #添加特效
    effect_duration=data.get("effect_duration",0)
    if effect_duration == 0:
        effect_duration=duration
        
    #添加字幕
    context.draft.add_subtitle(data.get("text",""))
    context.draft.add_effect(data.get("effect_name"), start=data.get("effect_start",0), duration=effect_duration)
    #添加图片
    context.draft.add_media(data.get("cur_image",""),duration=duration,transition_data=transition_data)
    audio=data.get("audio","")
    if audio != "":
        context.draft.add_media(audio,duration=duration)
    
    
def save(draft_name,datas) -> None:
    with DraftContext(draft_name) as context:
        for data in datas:
            add_media_item(context,data)
       