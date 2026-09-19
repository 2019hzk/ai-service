from typing import Any

from atguigu.app.schemas.run import AgentRunRequest
from atguigu.agent.harness.run.context import ContextCompiler
from atguigu.agent.harness.validator.output import OutputValidator, ValidatedAgentOutput


class AgentExecutor:

    def __init__(self, agent: Any):
        self.agent = agent
        self.context_compiler = ContextCompiler()
        self.output_validator = OutputValidator()

    async def execute(self, request: AgentRunRequest) -> ValidatedAgentOutput:
        """
        职责：执行agent
        1. 上下文构建器 构建上下文（消息+..）
        2. 调用Agent，Agent的输出
        3. 校验器 校验Agent输出(可信的结果)
        """
        # 1. 构建上下文(消息)
        messages = self.context_compiler.compile_messages(request)

        # 2.调用Agent
        raw_llm_output = await self.agent.ainvoke({"messages": messages})

        # 3. 提取结构化对象
        structured_llm_result = raw_llm_output['structured_response']

        # 3. 校验Agent输出
        validated_result = self.output_validator.validate(structured_llm_result)

        return validated_result
