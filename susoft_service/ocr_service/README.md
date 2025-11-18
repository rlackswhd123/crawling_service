# OCR 서비스 실행 가이드

## 1. 환경 설정

`.env` 파일 생성:
```bash
OCR_ENGINE=paddle
USE_LAYOUT=false
MAX_FILE_MB=20
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=3600
ENABLE_AUTH=false
AUTH_TOKEN=dev-secret-token-12345
HOST=0.0.0.0
PORT=8000
```

**인증 설정:**
- `ENABLE_AUTH=false`: 인증 비활성화 (로컬 개발용)
- `ENABLE_AUTH=true`: 인증 활성화 (운영 환경)

## 2. Redis 설치 및 실행

### Redis가 설치되어 있지 않은 경우

**macOS (Homebrew)**
```bash
brew install redis
brew services start redis
```

**Windows**
- Chocolatey: `choco install redis-64`
- 또는 공식 사이트에서 다운로드: https://redis.io/download

**Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

### Redis 실행

**Docker 사용 (권장)**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**로컬 Redis 실행**
```bash
redis-server
```

**설치 확인**
```bash
redis-cli ping
# 응답: PONG
```

**이미 Redis가 실행 중인 경우**
- "Address already in use" 오류가 나면 Redis가 이미 실행 중입니다
- 확인: `redis-cli ping` (PONG 응답이면 정상)
- 추가 실행 불필요, 바로 서버 실행 가능

## 3. 서버 실행

```bash
python run.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

## 4. API 테스트

### 방법 1: Swagger UI (가장 쉬움)
1. 브라우저에서 열기: http://localhost:8000/docs
2. 우측 상단 **"Authorize"** 버튼 클릭
3. Value 입력란에 토큰 입력 (`.env`의 `AUTH_TOKEN` 값):
   - **주의**: `Bearer ` 접두사 없이 토큰만 입력 (예: `dev-secret-token-12345`)
   - 자동으로 `Bearer`가 붙습니다
4. **"Authorize"** 클릭 → **"Close"** 클릭
5. `/ocr/extract` 엔드포인트 선택 → **"Try it out"** 클릭
6. 이미지 파일 업로드 및 파라미터 입력 후 **"Execute"** 클릭

**401 오류 발생 시 체크리스트:**
- 서버 재시작 여부 확인 (`.env` 변경 시 필요)
- 토큰에 공백이나 잘못된 문자가 없는지 확인
- `.env`의 `AUTH_TOKEN` 값과 입력한 토큰이 정확히 일치하는지 확인

### 방법 2: cURL
```bash
curl -X POST "http://localhost:8000/ocr/extract" \
  -H "Authorization: Bearer dev-secret-token-12345" \
  -F "idempotency_key=test_001" \
  -F "engine=paddle" \
  -F "use_layout=false" \
  -F "file=@test_image.jpg"
```

### 방법 3: Python 스크립트
```python
import requests

url = "http://localhost:8000/ocr/extract"
headers = {"Authorization": "Bearer dev-secret-token-12345"}
files = {"file": open("test_image.jpg", "rb")}
data = {
    "idempotency_key": "test_001",
    "engine": "paddle",
    "use_layout": False
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

## 5. Supabase 스키마 적용

`supabase_schema.sql` 파일을 Supabase SQL 에디터에서 실행하세요.

