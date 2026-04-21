"""
核心数据合约定义
产品、历史脚本、脚本生成输入/输出、视频分析输出的 Pydantic Schema
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# =============================================
# 产品信息
# =============================================


class ProductStatus(str, Enum):
    ON_SALE = "在售"
    OFF_SHELF = "下架"
    COMING_SOON = "即将上新"


class Product(BaseModel):
    """服装产品数据结构"""

    product_id: str = Field(..., description="产品唯一标识", examples=["SKU-2026-001"])
    name: str = Field(..., description="产品名称", examples=["白色高腰直筒裤"])
    category: str = Field(..., description="品类", examples=["裤装"])
    sub_category: Optional[str] = Field(None, description="子品类", examples=["直筒裤"])
    fabric: Optional[str] = Field(None, description="面料成分", examples=["97%棉 3%氨纶"])
    sizes: list[str] = Field(default_factory=list, description="可选尺码", examples=[["S", "M", "L", "XL"]])
    colors: list[str] = Field(default_factory=list, description="可选颜色", examples=[["白色", "米白"]])
    price: float = Field(..., description="售价（元）", examples=[199.0])
    original_price: Optional[float] = Field(None, description="原价（元）", examples=[399.0])
    selling_points: list[str] = Field(
        default_factory=list,
        description="核心卖点",
        examples=[["高腰设计拉长腿部比例", "直筒版型不挑腿型", "四面弹力穿着舒适"]],
    )
    target_audience: Optional[str] = Field(None, description="目标人群", examples=["25-35岁职场女性"])
    occasions: list[str] = Field(
        default_factory=list, description="适用场景", examples=[["通勤", "约会", "休闲"]]
    )
    images: list[str] = Field(default_factory=list, description="产品图片URL列表")
    description: Optional[str] = Field(None, description="详细产品描述")
    status: ProductStatus = Field(ProductStatus.ON_SALE, description="产品状态")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================
# 历史脚本
# =============================================


class Platform(str, Enum):
    DOUYIN = "抖音"
    XIAOHONGSHU = "小红书"
    KUAISHOU = "快手"
    BILIBILI = "B站"
    OTHER = "其他"


class ScriptMetrics(BaseModel):
    """脚本发布后的数据表现"""

    views: Optional[int] = Field(None, description="播放量")
    likes: Optional[int] = Field(None, description="点赞数")
    comments: Optional[int] = Field(None, description="评论数")
    shares: Optional[int] = Field(None, description="分享数")
    saves: Optional[int] = Field(None, description="收藏数")


class HistoricalScript(BaseModel):
    """历史脚本文案"""

    script_id: str = Field(..., description="脚本唯一标识", examples=["SCR-2026-001"])
    title: str = Field(..., description="脚本标题", examples=["白色裤子夏季穿搭"])
    platform: Platform = Field(..., description="发布平台")
    content: str = Field(..., description="完整脚本文本")
    video_url: Optional[str] = Field(None, description="原视频链接")
    publish_date: Optional[datetime] = Field(None, description="发布日期")
    metrics: Optional[ScriptMetrics] = None
    style_tags: list[str] = Field(
        default_factory=list,
        description="风格标签",
        examples=[["亲和力", "实用干货", "对比展示"]],
    )
    product_ids: list[str] = Field(default_factory=list, description="关联产品ID")
    duration_seconds: Optional[float] = Field(None, description="视频时长（秒）")
    created_at: Optional[datetime] = None


# =============================================
# 脚本生成 - 输入
# =============================================


class ScriptGenerationRequest(BaseModel):
    """脚本生成请求"""

    product_name: str = Field(..., description="新品名称", examples=["白色高腰直筒裤"])
    product_id: Optional[str] = Field(None, description="已有产品ID（如知识库中已有）")
    viral_video_ids: Optional[list[str]] = Field(
        None, description="参考爆款视频分析结果ID列表"
    )
    special_instructions: Optional[str] = Field(
        None,
        description="特别要求",
        examples=["突出性价比", "强调夏季透气"],
    )
    target_duration: Optional[int] = Field(
        45,
        description="目标时长（秒）",
        ge=15,
        le=180,
    )
    platform: Platform = Field(Platform.DOUYIN, description="目标平台")


# =============================================
# 脚本生成 - 输出
# =============================================


class ScriptSection(BaseModel):
    """脚本的某一段"""

    step: int = Field(..., description="步骤序号")
    step_name: str = Field(..., description="步骤名称", examples=["视觉钩子"])
    time_range: str = Field(..., description="预估时间范围", examples=["0-3秒"])
    visual: str = Field(..., description="画面描述")
    voiceover: str = Field(..., description="口播文案")
    purpose: str = Field(..., description="这段的目的说明")
    duration_seconds: float = Field(..., description="预估时长（秒）")


class StyleMatchScore(BaseModel):
    """风格匹配度评分"""

    overall_score: float = Field(..., description="总体风格匹配度 0-5", ge=0, le=5)
    tone_match: float = Field(..., description="语调匹配度 0-5", ge=0, le=5)
    vocabulary_match: float = Field(..., description="用词匹配度 0-5", ge=0, le=5)
    rhythm_match: float = Field(..., description="节奏匹配度 0-5", ge=0, le=5)
    reference_scripts_used: list[str] = Field(
        default_factory=list, description="参考的历史脚本ID列表"
    )


class ScriptGenerationResponse(BaseModel):
    """脚本生成结果"""

    request_id: str = Field(..., description="请求唯一标识")
    product_name: str = Field(..., description="产品名称")
    product_info_used: Optional[Product] = Field(None, description="使用的产品信息")
    sections: list[ScriptSection] = Field(
        ...,
        description="脚本各段内容（必须恰好4段）",
        min_length=4,
        max_length=4,
    )
    total_duration_seconds: float = Field(..., description="预估总时长（秒）")
    total_word_count: int = Field(..., description="总字数")
    style_match: Optional[StyleMatchScore] = None
    viral_references_used: list[str] = Field(
        default_factory=list, description="使用的爆款参考ID"
    )
    viral_patterns_applied: list[str] = Field(
        default_factory=list, description="应用的爆款模式"
    )
    quality_check_passed: bool = Field(..., description="是否通过质量检查")
    quality_issues: list[str] = Field(default_factory=list, description="质量问题列表")
    generated_at: datetime = Field(default_factory=datetime.now)


# =============================================
# 视频分析 - 输出
# =============================================


class HookType(str, Enum):
    PAIN_POINT = "痛点型"
    SUSPENSE = "悬念型"
    REVERSAL = "反转型"
    DATA = "数据型"
    CURIOSITY = "好奇型"
    VISUAL_IMPACT = "视觉冲击型"


class VideoScene(BaseModel):
    """视频场景/片段"""

    start_time: float = Field(..., description="开始时间（秒）")
    end_time: float = Field(..., description="结束时间（秒）")
    scene_index: int = Field(..., description="场景序号")


class VideoSectionAnalysis(BaseModel):
    """视频中某一段的分析"""

    time_range: str = Field(..., description="时间范围", examples=["0-3s"])
    text: str = Field(..., description="该段转录文案")
    analysis: str = Field(..., description="分析说明")
    score: float = Field(..., description="评分 1-10", ge=1, le=10)


class HookAnalysis(VideoSectionAnalysis):
    hook_type: Optional[HookType] = None
    technique: Optional[str] = Field(None, description="使用的钩子技巧")


class ContentAnalysis(VideoSectionAnalysis):
    persuasion_techniques: list[str] = Field(
        default_factory=list, description="使用的说服技巧"
    )
    emotional_arc: Optional[str] = Field(None, description="情感曲线描述")


class ValueAddAnalysis(VideoSectionAnalysis):
    value_type: Optional[str] = Field(None, description="价值类型", examples=["教学型", "分享型"])
    practical_tips: list[str] = Field(default_factory=list, description="提取的实用技巧")


class CTAAnalysis(VideoSectionAnalysis):
    action_type: Optional[str] = Field(None, description="引导的行为类型")
    urgency_technique: Optional[str] = Field(None, description="紧迫感技巧")


class ViralVideoAnalysis(BaseModel):
    """爆款视频分析结果"""

    video_url: str = Field(..., description="原始视频URL")
    title: Optional[str] = Field(None, description="原始视频标题")
    duration_seconds: float = Field(..., description="视频时长")
    transcript: str = Field(..., description="完整转录文稿")
    scenes: list[VideoScene] = Field(default_factory=list, description="场景切分")
    structure: dict = Field(
        ...,
        description="结构化分析：包含hook/content/value_add/cta四个key",
    )
    overall_analysis: str = Field(..., description="整体爆款原因总结")
    applicable_patterns: list[str] = Field(
        default_factory=list,
        description="可复制的爆款模式",
    )
    analyzed_at: datetime = Field(default_factory=datetime.now)


# =============================================
# 视频处理服务 - API 输出
# =============================================


class VideoProcessResponse(BaseModel):
    """视频处理服务返回"""

    video_url: str = Field(..., description="输入的视频URL")
    duration_seconds: float = Field(..., description="视频时长")
    transcript: str = Field(..., description="完整转录文本")
    segments: list[dict] = Field(
        default_factory=list,
        description="转录分段（含时间戳）",
    )
    scenes: list[VideoScene] = Field(default_factory=list, description="场景切分结果")
    keyframes: list[dict] = Field(
        default_factory=list,
        description="关键帧信息（时间戳+图片路径）",
    )
    status: str = Field("success", description="处理状态")
    error: Optional[str] = None
