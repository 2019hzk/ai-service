import jwt
from fastapi import HTTPException, status
from pydantic import ValidationError

from atguigu.app.schemas.auth import CurrentUser
from atguigu.common.config import get_settings


class AuthService:
    """解析 Customer Service 转发的用户 JWT。"""

    def __init__(self):
        self.settings = get_settings()

    def get_current_customer(
            self,
            authorization: str | None
    ) -> CurrentUser:

        # 1. 获取令牌
        token = self._extract_bearer_token(authorization)

        # 2. 获取当前用户
        current_user = self._decode_access_token(token)

        # 3. 校验当前用户的角色
        if current_user.role != "customer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有客户身份可以调用 AI Service"
            )
        return current_user

    @staticmethod
    def _extract_bearer_token(
            authorization: str | None
    ) -> str:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer Token 必须提供"
            )
        return authorization.split(" ", 1)[1]

    def _decode_access_token(self, token: str) -> CurrentUser:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm]
            )
            return CurrentUser.model_validate(payload)
        except (jwt.PyJWTError, ValidationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效令牌或者令牌过期"
            ) from exc
