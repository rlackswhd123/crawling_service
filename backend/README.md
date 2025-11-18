# 새움 AI 테스트공간 - Backend

FastAPI 기반 백엔드 서버

## 🚀 시작하기

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 입력
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 개발 모드 (hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는
python main.py
```

### 4. API 문서 확인

서버 실행 후:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
backend/
├── main.py                   # FastAPI 앱 엔트리포인트
├── routers/                  # API 라우터
│   ├── __init__.py
│   └── bangkku.py           # 방꾸 서비스 엔드포인트
├── services/                 # AI 서비스 로직
│   ├── __init__.py
│   ├── gemini_service.py    # Gemini 이미지 처리
│   └── veo3_service.py      # Veo3 비디오 생성
├── requirements.txt          # Python 의존성
├── .env.example             # 환경 변수 예시
└── README.md                # 이 파일
```

## 🔌 API 엔드포인트

### HTTP Endpoints

#### 1. 단일 이미지 처리

```
POST /api/bangkku/process-image
Content-Type: application/json

{
  "prompt": "Remove all furniture from this room",
  "image": "data:image/jpeg;base64,..."
}
```



#### 2. 다중 이미지 처리

```
POST /api/bangkku/process-multiple-images
Content-Type: application/json

{
  "prompt": "Create a 3D room visualization",
  "images": [
    "data:image/jpeg;base64,...",
    "data:image/jpeg;base64,...",
    "data:image/jpeg;base64,...",
    "data:image/jpeg;base64,..."
  ]
}
```



### WebSocket Endpoint

#### 비디오 생성 (실시간 진행률)

```
ws://localhost:8000/api/bangkku/ws/generate-video
```

**요청 메시지:**

```json
{
  "type": "generate",
  "prompt": "Slow camera pan across the room",
  "image": "data:image/jpeg;base64,...",
  "lastFrame": "data:image/jpeg;base64,..."  // optional
}
```

**응답 메시지:**

1. 진행률 업데이트:
   
   ```json
   {
   "type": "progress",
   "percent": 45,
   "message": "비디오 생성 중... (120초 경과)"
   }
   ```

2. 완료:
   
   ```json
   {
   "type": "completed",
   "result": {
    "video_url": "https://...",
    "thumbnail_url": "https://...",
    "duration": 10.0,
    "metadata": { ... }
   }
   }
   ```

3. 에러:
   
   ```json
   {
   "type": "error",
   "error": "Error message"
   }
   ```

## 🔧 서비스 상세

### Gemini Service

- **모델**: gemini-2.5-flash-preview-01-15
- **기능**: 이미지 처리 및 변환
- **평균 응답 시간**: 3-5초

### Veo3 Service

- **모델**: veo-3.1-flash-001
- **기능**: 비디오 생성
- **평균 생성 시간**: 2-10분
- **폴링 간격**: 10초
- **최대 대기 시간**: 10분

## 🔑 환경 변수

| 변수               | 설명                     | 필수                      |
| ---------------- | ---------------------- | ----------------------- |
| `GOOGLE_API_KEY` | Google AI Studio API 키 | ✅                       |
| `HOST`           | 서버 호스트                 | ❌ (기본값: 0.0.0.0)        |
| `PORT`           | 서버 포트                  | ❌ (기본값: 8000)           |
| `CORS_ORIGINS`   | CORS 허용 도메인            | ❌ (기본값: localhost:5173) |
| `LOG_LEVEL`      | 로그 레벨                  | ❌ (기본값: INFO)           |

## 📝 개발 가이드

### 새 서비스 추가

1. **서비스 파일 생성** (`services/new_service.py`)
   
   ```python
   class NewService:
    def __init__(self):
        # 초기화
        pass
   
    async def process(self, data):
        # 처리 로직
        pass
   ```

new_service = NewService()

```
2. **라우터 생성** (`routers/new_service.py`)

```python
from fastapi import APIRouter
from services import new_service

router = APIRouter()


@router.post("/process")
async def process(data: RequestModel):
    result = await new_service.process(data)
    return { "result": result }
```

3. **메인에 라우터 등록** (`main.py`)
   
   ```python
   from routers import new_service
   ```

app.include_router(
    new_service.router,
    prefix="/api/new-service",
    tags=["new-service"]
)

```
## 🐛 트러블슈팅

### API 키 오류
```

ValueError: GOOGLE_API_KEY environment variable is required

```
→ `.env` 파일에 `GOOGLE_API_KEY` 설정 확인

### CORS 오류
```

Access to fetch at '...' has been blocked by CORS policy

```
→ `main.py`의 `allow_origins`에 프론트엔드 URL 추가

### WebSocket 연결 실패
```

WebSocket connection failed

```
→ 방화벽 설정 확인, WebSocket 지원 여부 확인

## 📊 모니터링

### 로그 확인
```bash
# 실시간 로그 확인
tail -f logs/app.log

# 에러 로그만 확인
grep ERROR logs/app.log
```

### 헬스 체크

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/bangkku/health
```

## 🔗 관련 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Google Veo API](https://cloud.google.com/vertex-ai/generative-ai/docs/video/overview)
- [프로젝트 메인 README](../README.md)
