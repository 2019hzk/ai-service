import time
from time import perf_counter

from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.app.repositories.run import AgentRunRepository
from atguigu.app.schemas.run import AgentRunRequest
from atguigu.common.config import get_settings
from atguigu.common.utils import get_utcnow
from atguigu.harness.agent.run.events import build_response_event
from atguigu.harness.agent.run.executor import AgentExecutor
from atguigu.harness.agent.run.output import AgentRunOutPutMapper
from atguigu.models.models import AgentRun, AgentRunState


class AgentRunCoordinator:

    def __init__(self, session: AsyncSession, executor: AgentExecutor):
        self.setting = get_settings()
        self.session = session
        self.executor = executor
        self.agent_run_repo = AgentRunRepository(session)

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

        # 1. 创建AgentRun

        agent_run = AgentRun(
            conversation_id=request.conversation_id,
            user_id=user_id,
            turn_id=request.turn_id,
            state=AgentRunState.RUNNING,
            model_name=self.setting.llm_model,
            prompt_version="v1",
            input_context=request.model_dump(mode="json"),

        )
        # 2. 保存
        self.agent_run_repo.add_agent_run(agent_run)

        # 3. 提交
        await self.session.commit()

        # 4. 调用执行器执行以及映射AgentRunState对应的数据
        start_time = perf_counter()
        try:
            # a) 调用Agent执行获取可信的结果
            validated_result = await self.executor.execute(request)
            # b) 将可信的结果映射到不同AgentRunState中
            agent_run.state, agent_run.result = AgentRunOutPutMapper.map(validated_result)
        except Exception as e:
            agent_run.latency_ms = int(perf_counter() - start_time) * 1000
            agent_run.error = str(e)
            agent_run.state = AgentRunState.FAILED
            agent_run.finished_at = get_utcnow()

        # 5. 调用响应事件构建器构建返回给customer-service的数据
        await self.session.commit()  # session是同一个，且拥有agent_run，那么直接会修改
        return build_response_event(agent_run)

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


if __name__ == '__main__':
    start = perf_counter()
    time.sleep(2)
    end = perf_counter()
    print(int(end - start) * 1000)
