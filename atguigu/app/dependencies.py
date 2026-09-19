from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.app.services.auth import AuthService
from atguigu.common.config import get_settings
from atguigu.harness.agent.run.coordinator import AgentRunCoordinator
from atguigu.harness.agent.run.executor import AgentExecutor
from atguigu.infrastructure.db import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_auth_service() -> AuthService:
    return AuthService()


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_agent_executor(request: Request)->AgentExecutor:
    return AgentExecutor(agent=request.app.state.agent)


AgentExecutorDep = Annotated[AgentExecutor, Depends(get_agent_executor)]


def require_internal_service(token: Annotated[str | None, Header(alias="X-Internal-Service-Token")] = None):
    """只允许 Customer Service 调用内部接口。"""
    if token != get_settings().internal_service_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid internal service token"
        )


def get_agent_coordinator(session: SessionDep,
                          executor: AgentExecutorDep
                          ):
    return AgentRunCoordinator(session=session, executor=executor)


AgentRunCoordinatorDep = Annotated[AgentRunCoordinator, Depends(get_agent_coordinator)]
