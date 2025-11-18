# 환경 변수 설정 템플릿

`.env` 파일을 프로젝트 루트에 생성하고 아래 내용을 참고하여 설정하세요.

```env
# OCR Configuration
OCR_ENGINE=paddle
USE_LAYOUT=false
MAX_FILE_MB=20

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=3600

# Authentication
ENABLE_AUTH=true
AUTH_TOKEN=your-secret-token-here

# Google Cloud Vision (Optional)
# GCP 프로젝트 ID
GCP_PROJECT=your-project-id

# GCP 서비스 계정 키 JSON 파일 경로 또는 JSON 문자열
# 파일 경로 예시: /path/to/service-account-key.json
# JSON 문자열 예시: {"type":"service_account","project_id":"..."}
GCP_CREDENTIALS_JSON=/path/to/google_vision_key.json

# Database (Optional - 읽기 전용)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## 설정 방법

### 1. 기본 설정 (PaddleOCR만 사용)
```env
ENABLE_AUTH=false
REDIS_URL=redis://localhost:6379
```

### 2. Google Cloud Vision 추가 설정
1. Google Cloud Console에서 서비스 계정 키 JSON 파일 다운로드
2. 프로젝트 디렉토리에 키 파일 저장 (예: `google_vision_key.json`)
3. `.env` 파일에 다음 추가:
```env
GCP_PROJECT=your-actual-project-id
GCP_CREDENTIALS_JSON=/Users/macpro2019/Desktop/ocr_test/google_vision_key.json
```

### 3. 보안 주의사항
- `.env` 파일과 `google_vision_key.json`은 절대 Git에 커밋하지 마세요
- `.gitignore`에 다음 항목이 포함되어 있는지 확인하세요:
  ```
  .env
  *.json
  !package.json
  ```

