"""
FastAPI Main Application
새움 AI 테스트공간 백엔드
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드 (다른 import보다 먼저!)
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import bangkku
from routers import prompt_router, test_result_router
from database.connection import DatabaseConnection

app = FastAPI(
    title="새움 AI 테스트공간",
    description="Bangkku, AniTalk, BAIK 서비스 통합 API",
    version="1.0.0"
)

# CORS 설정 - 환경변수에서 읽기
# cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:12345", "https://localhost:8501", "http://localhost:8501")
# cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=cors_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

cors_origins_str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:12345,http://localhost:12346,https://localhost:8501,http://localhost:8501,https://anytalk.com"
)
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files 설정
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)  # 디렉토리가 없으면 생성
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")



# Startup/Shutdown Events
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작시 DB 연결 풀 초기화"""
    DatabaseConnection.initialize_pool()
    print("✅ Database connection pool initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료시 DB 연결 풀 해제"""
    DatabaseConnection.close_pool()
    print("✅ Database connection pool closed")


# 라우터 등록
app.include_router(bangkku.router, prefix="/api/bangkku", tags=["bangkku"])
app.include_router(prompt_router.router)  # prefix already set in router
app.include_router(test_result_router.router)  # prefix already set in router

@app.get("/")
async def root():
    return {
        "service": "새움 AI 테스트공간",
        "version": "1.0.0",
        "services": ["bangkku", "anitalk", "baik"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    # 환경변수에서 host와 port 읽기
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 12346))

    print(f"🚀 Starting server on {host}:{port}")
    print(f"📡 CORS origins: {cors_origins}")

    uvicorn.run(app, host=host, port=port)
