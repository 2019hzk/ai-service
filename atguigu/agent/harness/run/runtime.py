from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRuntimeContext:
    """提供给 Agent 和业务工具的单次运行信息"""

    run_id: str
    conversation_id: str
    user_id: str
    access_token: str



