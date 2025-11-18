"""FastAPI Main Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.cache.idempotency import idempotency_cache
from app.api import ocr


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    await idempotency_cache.connect()
    yield
    # 종료 시
    await idempotency_cache.disconnect()


app = FastAPI(
    title="OCR Microservice",
    description="조건부 OCR 서비스 (무상태, 계산 전용)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ocr.router)


@app.get("/", tags=["Health"])
async def root():
    """헬스 체크"""
    return {
        "status": "ok",
        "service": "OCR Microservice",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health():
    """헬스 체크 (상세)"""
    return {
        "status": "ok",
        "engine": settings.ocr_engine,
        "use_layout": settings.use_layout,
        "max_file_mb": settings.max_file_mb
    }


@app.get("/debug/config", tags=["Debug"])
async def debug_config():
    """디버그: 현재 설정 확인 (개발용)"""
    return {
        "auth_token": settings.auth_token,
        "auth_token_length": len(settings.auth_token),
        "auth_token_repr": repr(settings.auth_token)
    }

