"""Authentication Middleware"""
import logging
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)  # 인증 비활성화 시 에러 발생 안 함


async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)):
    """Bearer 토큰 검증 (인증 비활성화 시 건너뜀)"""
    # 인증이 비활성화된 경우
    if not settings.enable_auth:
        return None
    
    # 인증이 활성화되었지만 토큰이 없는 경우
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 검증
    received_token = credentials.credentials.strip()
    expected_token = settings.auth_token.strip()
    
    if received_token != expected_token:
        error_detail = f"Token mismatch (received length: {len(received_token)}, expected length: {len(expected_token)})"
        logger.warning(f"Auth failed: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

