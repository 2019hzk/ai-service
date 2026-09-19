from typing import Any

from atguigu.common.utils import get_uid
from atguigu.agent.harness.validator.output import ValidatedAgentOutput
from atguigu.agent.llm.output import ReplyType
from atguigu.models.models import AgentRunState


class AgentRunOutPutMapper:

    @staticmethod
    def map(validated_result: ValidatedAgentOutput) -> tuple[AgentRunState, dict[str, Any]]:
        """
        职责：根据可信的llm回复的类型，映射Agent不同状态需要的数据
        Agent:state:RUNNING---->Agent状态需要的数据
        Agent:state:HANDED_OFF--->Agent状态需要的数据

        ....
        """

        if validated_result.reply_type == ReplyType.ANSWER:
            return AgentRunState.COMPLETED, AgentRunOutPutMapper._build_agent_output(validated_result)

        if validated_result.reply_type == ReplyType.CLARIFY:
            return AgentRunState.COMPLETED, AgentRunOutPutMapper._build_agent_output(validated_result)

        if validated_result.reply_type == ReplyType.DECLINE:
            return AgentRunState.COMPLETED, AgentRunOutPutMapper._build_agent_output(validated_result)

        if validated_result.reply_type == ReplyType.REQUEST_HANDOFF:
            return AgentRunState.HANDED_OFF, AgentRunOutPutMapper._build_handoff_output(validated_result)

        raise ValueError("不支持的回复类型")

    @classmethod
    def _build_agent_output(cls,
                            validated_result: ValidatedAgentOutput) -> dict[str, Any]:
        return {
            "message_id": get_uid("msg"),
            "content": {
                "text": validated_result.reply_content,
                "reply_type": validated_result.reply_type
            }
        }

    @classmethod
    def _build_handoff_output(cls, validated_result: ValidatedAgentOutput) -> dict[str, Any]:
        return {
            "reason_code": validated_result.handoff_request.reason_code,
            # customer-service目前没有用【summary:给客服，message:给用户】
            "summary": validated_result.handoff_request.summary,
            "message": validated_result.reply_content
        }
