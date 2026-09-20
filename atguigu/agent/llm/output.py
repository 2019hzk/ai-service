from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator


class ReplyType(StrEnum):
    """Agent 本轮生成的回复类型。"""

    ANSWER = "ANSWER"
    CLARIFY = "CLARIFY"
    DECLINE = "DECLINE"
    REQUEST_HANDOFF = "REQUEST_HANDOFF"


class HandoffReason(StrEnum):
    """转人工的业务原因。"""

    USER_REQUESTED = "USER_REQUESTED"
    COMPLAINT = "COMPLAINT"
    RISK_REVIEW = "RISK_REVIEW"


class HandoffRequest(BaseModel):
    """定义 Customer Service 创建人工工单需要的信息。"""

    reason_code: HandoffReason = Field(description="创建人工工单使用的转人工原因")
    summary: str = Field(
        min_length=1,
        max_length=500,
        description="面向人工客服的问题摘要"
    )


class PageActionRequest(BaseModel):
    """定义 Agent 建议用户前往页面完成的操作意图。"""

    action_code: str
    resource_id: str


class AgentOutput(BaseModel):
    """定义大语言模型必须返回的结构化结果。"""

    reply_type: ReplyType = Field(description="本轮客服回复的业务类型")
    reply_content: str = Field(min_length=1, max_length=4000, description="可以直接展示给用户的完整回复内容")
    handoff_request: HandoffRequest | None = Field(default=None, description="仅请求转人工时提供的工单信息")
    # page_action_request: PageActionRequest | None = Field(default=None, description="仅正常回答需要引导用户前往页面时提供"
    # )
