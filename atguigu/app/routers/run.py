from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from atguigu.app.dependencies import (
    AuthServiceDep,
    require_internal_service, AgentRunCoordinatorDep
)
from atguigu.app.schemas.run import AgentRunRequest

router = APIRouter(prefix="/internal/v1/agent", tags=["AI Run"])


@router.post("/runs")
async def start_run(
        request: AgentRunRequest,
        auth_service: AuthServiceDep,
        _: Annotated[None, Depends(require_internal_service)],
        agent_coordinator: AgentRunCoordinatorDep,
        authorization: Annotated[str | None, Header()] = None,

) -> dict:
    current_user = auth_service.get_current_customer(authorization)
    access_token = auth_service.get_bearer_token(authorization)
    return await agent_coordinator.start_run(current_user.user_id, access_token, request)


@router.post("/runs/{run_id}/confirm")
async def confirm_run(
        run_id: str,
        auth_service: AuthServiceDep,
        agent_coordinator: AgentRunCoordinatorDep,
        _: Annotated[None, Depends(require_internal_service)],
        authorization: Annotated[str | None, Header()] = None
) -> dict:
    current_user = auth_service.get_current_customer(authorization)
    return await agent_coordinator.confirm_run(current_user.user_id, run_id)


@router.post(
    "/runs/{run_id}/cancel",
    status_code=204  # 接口正常返回 响应体没有任何的数据（比200更精准）
)
async def cancel_run(
        run_id: str,
        agent_coordinator: AgentRunCoordinatorDep,
        auth_service: AuthServiceDep,
        _: Annotated[None, Depends(require_internal_service)],
        authorization: Annotated[str | None, Header()] = None
):
    current_user = auth_service.get_current_customer(authorization)
    await agent_coordinator.confirm_run(current_user.user_id, run_id)
