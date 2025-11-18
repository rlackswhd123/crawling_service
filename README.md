# 새움 AI 플레이그라운드

새움소프트 AI 서비스 통합 테스트 및 실험 플랫폼

## 📖 프로젝트 소개

이 프로젝트는 새움소프트에서 개발 중인 AI 기반 서비스들을 통합 관리하고 테스트하기 위한 플레이그라운드입니다. 각 서비스별 AI 기능을 독립적으로 실험하고 검증할 수 있는 환경을 제공합니다.

### 서비스 목록

#### 🛋️ 방꾸 (Bangkku)

인테리어 디자인을 위한 AI 이미지 처리 서비스

**주요 기능**:

- **가구 제거**: 방 사진에서 가구를 자동으로 제거하여 빈 공간 시각화
- **가구 정면 샷 변환**: 다양한 각도의 가구 이미지를 정면 뷰로 변환
- **3D 룸 생성**: 2D 가구 배치도를 3D 공간으로 변환
- **비디오 생성**: 정적 이미지를 동적 비디오로 변환 (Veo3.1)

#### 📱 애니톡 (AniTalk)

*Coming Soon* - AI 기반 애니메이션 대화 서비스

#### 🤖 BAIK

*Coming Soon* - AI 어시스턴트 서비스

---

## 🏗️ 기술 스택

### Frontend

- **Framework**: Vue 3.5.22 (Composition API)
- **Language**: TypeScript 5.9.3
- **Build Tool**: Vite 7.1.7
- **UI Library**: shadcn-vue (Tailwind CSS 4.1.14 기반)
- **State Management**: Vue Composition API
- **Routing**: Vue Router 4.x

### Backend

- **Framework**: FastAPI 0.115.0
- **Language**: Python 3.13
- **WebSocket**: WebSockets 13.1
- **ASGI Server**: Uvicorn 0.32.0

### AI Services

- **Google Gemini**: `@google/genai` 1.21.0
  - Gemini 2.5 Flash Image Preview (이미지 처리)
- **Google Veo3**: `google-genai` ≥1.45.0
  - Veo 3.1 Generate Preview (비디오 생성)
- **Utilities**:
  - `python-multipart` (파일 업로드)

---

## 📁 프로젝트 구조

```
saeum-ai-api/
├── frontend/                    # Vue 3 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/             # shadcn-vue 컴포넌트
│   │   │   ├── layout/         # 레이아웃 (사이드바, 헤더)
│   │   │   └── bangkku/         # 방꾸 AI 기능 컴포넌트
│   │   ├── services/           # AI 서비스 통신 레이어
│   │   │   ├── gemini.service.ts
│   │   │   ├── veo3.service.ts
│   │   │   └── video-api.service.ts
│   │   ├── utils/              # 유틸리티 함수
│   │   ├── types/              # TypeScript 타입 정의
│   │   ├── router/             # Vue Router 설정
│   │   ├── views/              # 페이지 컴포넌트
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── backend/                     # FastAPI 백엔드
│   ├── main.py                 # FastAPI 애플리케이션
│   ├── services/               # AI 서비스 모듈
│   │   ├── gemini_service.py
│   │   └── veo3_service.py
│   ├── routers/                # API 라우터
│   │   ├── bangkku.py           # /api/bangkku/*
│   │   ├── anitalk.py          # /api/anitalk/*
│   │   └── baik.py             # /api/baik/*
│   ├── utils/
│   │   └── timer.py
│   └── requirements.txt
├── claudedocs/                  # AI 개발 문서
│   ├── prompts.md              # 프롬프트 버전 관리
│   ├── architecture.md         # 시스템 아키텍처
│   └── api-reference.md        # API 명세서
├── README.md
└── CLAUDE.md                    # AI 개발 가이드
```

---

## 🚀 설치 및 실행

### 사전 요구사항

- Node.js 20.x 이상
- Python 3.13
- Google Cloud API 키 (Gemini, Veo3)

### 1. 저장소 클론

```bash
git clone <repository-url>
cd saeum-ai-api
```

### 2. 환경 변수 설정

#### Frontend 환경변수

`frontend/.env` 파일 생성 (또는 `.env.example` 복사):

```bash
# Google Gemini API Key
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Backend API URL (without protocol)
VITE_API_URL=localhost:12346
```

#### Backend 환경변수

`backend/.env` 파일 생성 (또는 `.env.example` 복사):

```bash
# Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=12346

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:12345,http://localhost:5173,http://localhost:3000
```

### 3. 프론트엔드 설정

```bash
cd frontend
npm install
npm run dev
```

프론트엔드는 `http://localhost:12345`에서 실행됩니다.

### 4. 백엔드 설정

```bash
cd backend
pip install -r requirements.txt

# 방법 1: Python으로 직접 실행 (환경변수 자동 적용)
python main.py

# 방법 2: uvicorn으로 실행 (포트 명시)
uvicorn main:app --reload --port 12346
```

백엔드는 `http://localhost:12346`에서 실행됩니다 (환경변수로 변경 가능).

---

## 🔌 API 엔드포인트

### 방꾸 (Bangkku) - `/api/bangkku`

| 엔드포인트                               | 메서드      | 설명         |
| ----------------------------------- | -------- | ---------- |
| `/api/bangkku/furniture-removal`    | POST, WS | 가구 제거      |
| `/api/bangkku/furniture-front-view` | POST, WS | 가구 정면 샷 변환 |
| `/api/bangkku/3d-room-generator`    | POST, WS | 3D 룸 생성    |
| `/api/bangkku/video-generation`     | POST, WS | 비디오 생성     |

### 애니톡 (AniTalk) - `/api/anitalk`

*Coming Soon*

### BAIK - `/api/baik`

*Coming Soon*

### WebSocket 엔드포인트

- `/ws/generate-video` - 실시간 비디오 생성 진행률 업데이트

자세한 API 명세는 [`claudedocs/api-reference.md`](./claudedocs/api-reference.md)를 참고하세요.

---

## 🎨 UI 구조

### 사이드바 네비게이션

```
[새움 AI 플레이그라운드]

📦 방꾸
  ├── 🛋️ 가구 제거
  ├── 🖼️ 가구 정면 샷 변환
  ├── 🏠 3D 룸 생성
  └── 🎬 비디오 생성

📱 애니톡 (Coming Soon)

🤖 BAIK (Coming Soon)

ㅇㅇ
```

### 라우팅

| 경로                              | 기능              |
| ------------------------------- | --------------- |
| `/bangkku/furniture-removal`    | 가구 제거           |
| `/bangkku/furniture-front-view` | 가구 정면 샷 변환      |
| `/bangkku/3d-room-generator`    | 3D 룸 생성         |
| `/bangkku/video-generation`     | 비디오 생성          |
| `/anitalk/*`                    | Coming Soon 페이지 |
| `/baik/*`                       | Coming Soon 페이지 |

---

## 🧪 개발 가이드

### AI 프롬프트 관리

모든 AI 프롬프트는 [`claudedocs/prompts.md`](./claudedocs/prompts.md)에서 버전 관리됩니다.

**프롬프트 작성 규칙**:

- 각 기능별로 버전 히스토리 유지
- 변경 사유 및 결과 문서화
- 성공한 프롬프트는 `v{숫자}` 태그로 관리

### WebSocket 통신 패턴

장시간 실행되는 AI 작업(비디오 생성 등)은 WebSocket을 사용합니다:

```typescript
// 클라이언트 (Vue)
const ws = new WebSocket('ws://localhost:12346/ws/generate-video');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'progress':
      updateProgress(data.percent);
      break;
    case 'completed':
      handleResult(data.result);
      break;
    case 'error':
      handleError(data.error);
      break;
  }
};
```



### 코드 스타일

- **Frontend**: ESLint + Prettier (Vue 3 스타일 가이드 준수)
- **Backend**: Black + isort (PEP 8 준수)
- **TypeScript**: Strict 모드 활성화
- **Naming**:
  - Components: PascalCase (`FurnitureRemoval.vue`)
  - Services: camelCase (`gemini.service.ts`)
  - Routes: kebab-case (`/furniture-removal`)

---

## 🔧 트러블슈팅

### 프론트엔드 빌드 오류

```bash
# 캐시 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### 백엔드 실행 오류

```bash
# 가상환경 재생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### API 키 오류

`.env` 파일에 올바른 Google Cloud API 키가 설정되어 있는지 확인하세요.

---

## 📝 라이선스

Copyright © 2025 새움소프트. All rights reserved.

---
