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

    reason_code: HandoffReason
    summary: str = Field(min_length=1, max_length=500)


class PageActionRequest(BaseModel):
    """定义 Agent 建议用户前往页面完成的操作意图。"""

    action_code: str
    object_type: str


class AgentOutput(BaseModel):
    """定义大语言模型必须返回的结构化结果。"""

    reply_type: ReplyType
    reply_content: str = Field(min_length=1, max_length=4000)
    handoff_request: HandoffRequest | None = None
    page_action_request: PageActionRequest | None = None
