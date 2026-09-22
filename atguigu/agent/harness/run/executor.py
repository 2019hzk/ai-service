from typing import Any

from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from pydantic import ValidationError

from atguigu.agent.harness.errors import AgentExecutionError, AgentOutputValidationError, TerminalErrorCode, \
    CorrectableErrorCode
from atguigu.agent.harness.rules.correction import OutputCorrectionRules
from atguigu.agent.harness.run.runtime import AgentRuntimeContext
from atguigu.agent.llm.adapter import ModelAdapter
from atguigu.agent.llm.output import AgentOutput, ReplyType
from atguigu.app.schemas.run import AgentRunRequest
from atguigu.agent.harness.run.context import ContextCompiler
from atguigu.agent.harness.validator.output import AgentOutputValidator, ValidatedAgentOutput


class AgentExecutor:

    def __init__(self, agent: Any, output_validator: AgentOutputValidator):
        self.agent = agent
        self.context_compiler = ContextCompiler()
        self.output_validator = output_validator

    async def execute(self,
                      request: AgentRunRequest,
                      runtime_context: AgentRuntimeContext) -> ValidatedAgentOutput:
        """
        职责：执行 Agent 调用，并对可纠正的输出错误有限重试。
        1. 上下文构建器 构建上下文（消息+..）
        2. 调用Agent，Agent的输出
        3. 校验器 校验Agent输出(可信的结果)
        """
        # 1. 构建上下文(消息)
        messages = self.context_compiler.compile_messages(request)

        # 2. 执行带有明确次数上限的 Agent 生成和纠错
        return await self._execute_with_correction(
            messages,
            runtime_context
        )

    async def _execute_with_correction(
            self,
            messages: list[Any],
            runtime_context: AgentRuntimeContext
    ) -> ValidatedAgentOutput:
        """执行 Agent，并在允许范围内纠正输出。"""

        # 1. 执行首次生成以及配置允许的有限纠错
        for attempt in range(2):
            try:
                # a. 调用 Agent 并保留完整执行过程
                raw_agent_output = await self._invoke_agent(messages, runtime_context)

                # b. 解析结构化结果并执行服务端输出校验
                normalized_agent_output = self._normalize_agent_output(raw_agent_output)

                return await self._validate_agent_output(
                    normalized_agent_output,
                    runtime_context.run_id
                )
            except ToolCallLimitExceededError:
                # c. 工具超限时使用固定拒绝结果完成当前 Run
                return self._build_tool_limit_output()

            except AgentOutputValidationError as exc:
                # d. 处理输出错误并生成下一轮纠错消息
                messages = self._handle_output_validation_error(
                    raw_agent_output,
                    exc,
                    attempt
                )

    async def _invoke_agent(
            self,
            messages: list[Any],
            runtime_context: AgentRuntimeContext
    ) -> Any:
        """调用共享 Agent，并处理调用异常和工具超限"""
        try:
            # 1. 使用当前模型消息和运行上下文调用 Agent
            return await self.agent.ainvoke({"messages": messages}, context=runtime_context)
        except ToolCallLimitExceededError:
            # 2. 将工具超限交给执行主流程生成安全结果
            raise
        except Exception as exc:
            # 3. 将模型服务和 Agent 调用异常转换成执行错误
            raise AgentExecutionError(
                TerminalErrorCode.MODEL_CALL_FAILED,
                "模型调用失败"
            ) from exc

    @staticmethod
    def _normalize_agent_output(raw_output: Any) -> AgentOutput:
        """提取并校验 Agent 返回的结构化结果"""
        try:
            # 1. 使用模型适配器提取 AgentOutput
            return ModelAdapter.normalize_output(raw_output)
        except ValidationError as exc:
            # 2. 将结构不完整结果转换成可纠正的输出错误
            raise AgentOutputValidationError(
                CorrectableErrorCode.MODEL_OUTPUT_INVALID,
                "模型返回的结构化结果不符合约定"
            ) from exc

    async def _validate_agent_output(self, output: AgentOutput, run_id: str) -> ValidatedAgentOutput:
        """执行回答事实和页面动作的服务端校验"""
        try:
            # 1. 使用当前 Run 的工具证据校验 Agent 输出
            return await self.output_validator.validate(output, run_id)

        except AgentOutputValidationError:
            # 2. 保留可识别的业务校验错误供执行器纠错
            raise
        except Exception as exc:
            # 3. 将校验器内部未知异常转换成统一执行错误
            raise AgentExecutionError(
                TerminalErrorCode.OUTPUT_VALIDATION_FAILED,
                "Agent 输出校验失败"
            ) from exc

    @staticmethod
    def _build_tool_limit_output() -> ValidatedAgentOutput:
        """构建工具调用次数超限后的固定拒绝结果"""
        # 1. 返回不包含业务事实和页面动作的可信安全回复
        return ValidatedAgentOutput(
            reply_type=ReplyType.DECLINE,
            reply_content=(
                "本次查询调用业务工具次数过多，"
                "暂时无法完成查询。"
            )
        )

    def _handle_output_validation_error(
            self,
            raw_output: Any,
            error: AgentOutputValidationError,
            attempt: int
    ) -> list[Any]:
        """处理输出校验错误，并返回下一轮纠错消息"""

        # 1. 不可纠正或纠错次数耗尽时终止当前 Run
        is_last_attempt = attempt == 2
        if (
                is_last_attempt
                or not OutputCorrectionRules.can_correct(error)
        ):
            raise AgentExecutionError(
                error.code,
                str(error)
            ) from error

        # 2. 保留本轮轨迹并追加纠错反馈
        return [
            *raw_output["messages"],
            OutputCorrectionRules.build_feedback(error)
        ]
