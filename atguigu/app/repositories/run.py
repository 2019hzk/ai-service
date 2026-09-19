from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.models.models import AgentRun


class AgentRunRepository:
    """封装 AgentRun 的持久化操作。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def add_agent_run(self, agent_run: AgentRun):
        self.session.add(agent_run)
