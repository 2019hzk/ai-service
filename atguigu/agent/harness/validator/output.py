from atguigu.agent.llm.output import AgentOutput, ReplyType


class ValidatedAgentOutput(AgentOutput):
    pass


class OutputValidator:

    def validate(self, llm_output: AgentOutput) -> ValidatedAgentOutput:
        """
        目前暂时不做校验以及返回校验后的结果对象
        llm_output：
        """
        return ValidatedAgentOutput(reply_type=ReplyType.ANSWER, reply_content="我已经查询到订单为001的状态是已支付")
