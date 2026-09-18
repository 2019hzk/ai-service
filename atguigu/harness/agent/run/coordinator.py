from atguigu.app.schemas.run import AgentRunRequest


class AgentRunCoordinator:

    async def start_run(self,
                        user_id: str,
                        request: AgentRunRequest) -> dict:
        """
        职责：
        1. 创建AgentRun
        2. AgentDecision(决策结构化对象：BaseModel做检验)=调用LLM/执行工具（AgentExecutor）
        3. 根据决策判断逻辑（）
        4. 根据判断逻辑的结果，构建不同事件类型响应数据
        5. 返回出去
        """
        # pass
        return {}

    async def confirm_run(self,
                          user_id: str,
                          run_id: str) -> dict:
        """
        核心职责：
        1. 从start_run中将决策的结果 获取到
        2. 修改AgentRun的状态（COMPLETED）
        3. 返回结果
        """
        return {}

    async def cancel_run(self,
                         user_id: str,
                         run_id: str
                         ):
        """
            核心职责：
            修改AgentRun的状态（SUPERSEDED）
        """
