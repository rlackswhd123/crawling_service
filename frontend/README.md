# 새움 AI 플레이그라운드 - Frontend

Vue 3 + TypeScript 기반 AI 서비스 통합 테스트 플랫폼 프론트엔드

## 📖 프로젝트 소개

새움소프트의 AI 서비스들을 위한 통합 웹 인터페이스입니다. Vue 3 Composition API와 TypeScript를 기반으로 구축되었으며, Google Gemini 및 Veo3 AI 모델과의 실시간 통신을 지원합니다.

### 제공 기능

#### 🛋️ 방꾸 (Bangkku) AI 서비스

- **가구 제거**: 방 사진에서 가구를 자동으로 제거 (배치 처리 지원, 최대 10개)
- **가구 정면 샷 변환**: 다양한 각도의 가구 이미지를 카탈로그용 정면 뷰로 변환
- **3D 룸 생성**: 2D 가구 배치도를 사실적인 3D 공간으로 렌더링 (구조 선택: ㅡ자/ㄱ자/ㄷ자)
- **비디오 생성**: 정적 이미지를 동적 비디오로 변환 (WebSocket 실시간 진행률)

#### 📱 애니톡 (AniTalk)

*Coming Soon* - AI 기반 애니메이션 대화 서비스

#### 🤖 BAIK

*Coming Soon* - AI 어시스턴트 서비스

---

## 🏗️ 기술 스택

### Core

- **Framework**: Vue 3.5.22 (Composition API)
- **Language**: TypeScript 5.9.3 (Strict Mode)
- **Build Tool**: Vite 7.1.7

### UI & Styling

- **UI Library**: shadcn-vue (reka-ui 2.6.0)
- **CSS Framework**: Tailwind CSS 4.1.14
- **Animation**: tw-animate-css 1.4.0
- **Icons**: lucide-vue-next 0.548.0
- **Font**: Pretendard Variable 1.3.9

### State & Routing

- **State Management**: Vue Composition API (ref, computed, reactive)
- **Router**: Vue Router 4.6.3
- **Composables**: @vueuse/core 14.0.0

### AI Integration

- **Google Gemini**: @google/genai 1.21.0
  - Image editing (Gemini 2.5 Flash)
  - Multi-image processing

### Utilities

- **Class Management**: clsx 2.1.1, tailwind-merge 3.3.1
- **Variants**: class-variance-authority 0.7.1
- **Screenshot**: modern-screenshot 4.6.6

---

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── assets/                      # 정적 리소스
│   │   ├── room-default/            # 기본 이미지 (테스트용)
│   │   └── ...
│   ├── components/
│   │   ├── ui/                      # shadcn-vue 컴포넌트 (수정 금지)
│   │   │   ├── button/
│   │   │   ├── card/
│   │   │   ├── select/
│   │   │   └── ...
│   │   └── layout/                  # 레이아웃 컴포넌트
│   │       ├── AppSidebar.vue       # 사이드바 네비게이션
│   │       └── ...
│   ├── services/                    # API 통신 레이어
│   │   └── bangkku/
│   │       ├── gemini.service.ts    # Gemini 이미지 처리
│   │       └── veo3.service.ts      # Veo3 비디오 생성
│   ├── types/                       # TypeScript 타입 정의
│   │   ├── room3d.types.ts          # 3D 룸 타입
│   │   └── ...
│   ├── utils/                       # 유틸리티 함수
│   │   ├── room3d-prompts.ts        # 동적 프롬프트 생성
│   │   └── ...
│   ├── views/                       # 페이지 컴포넌트
│   │   ├── bangkku/
│   │   │   ├── FurnitureRemoval.vue      # 가구 제거 (배치)
│   │   │   ├── FurnitureFrontView.vue    # 가구 정면 샷
│   │   │   ├── Room3DGenerator.vue       # 3D 룸 생성
│   │   │   └── VideoGenerator.vue        # 비디오 생성
│   │   └── ComingSoon.vue           # Coming Soon 페이지
│   ├── router/
│   │   └── index.ts                 # 라우팅 설정
│   ├── style.css                    # Tailwind + 전역 스타일
│   ├── App.vue                      # 루트 컴포넌트
│   └── main.ts                      # 애플리케이션 엔트리
├── public/
├── index.html
├── package.json
├── vite.config.ts                   # Vite 설정
├── tailwind.config.js
└── tsconfig.json
```

---

## 🚀 설치 및 실행

### 사전 요구사항

- **Node.js**: 20.x 이상
- **npm** 또는 **yarn**
- **Google Gemini API Key**: [Google AI Studio](https://ai.google.dev/)에서 발급

### 1. 환경 변수 설정

프로젝트 루트 또는 `frontend/` 폴더에 `.env` 파일 생성:

```bash
# Google Gemini API Key
VITE_GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. 의존성 설치

```bash
cd frontend
npm install
```

### 3. 개발 서버 실행

```bash
npm run dev
```

프론트엔드는 `http://localhost:12345`에서 자동 실행됩니다.

### 4. 프로덕션 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

### 5. 빌드 미리보기

```bash
npm run preview
```

---

## 🎨 UI/UX 구조

### 라우팅

| 경로                              | 컴포넌트                   | 기능                                 |
| ------------------------------- | ---------------------- | ---------------------------------- |
| `/`                             | (Redirect)             | `/bangkku/furniture-removal`로 리디렉션 |
| `/bangkku/furniture-removal`    | FurnitureRemoval.vue   | 가구 제거 (배치)                         |
| `/bangkku/furniture-front-view` | FurnitureFrontView.vue | 가구 정면 샷 변환                         |
| `/bangkku/3d-room-generator`    | Room3DGenerator.vue    | 3D 룸 생성                            |
| `/bangkku/video-generation`     | VideoGenerator.vue     | 비디오 생성                             |
| `/anitalk/*`                    | ComingSoon.vue         | 애니톡 (준비 중)                         |
| `/baik/*`                       | ComingSoon.vue         | BAIK (준비 중)                        |

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
```

---

## 🔧 개발 가이드

### 아키텍처 패턴

#### 서비스 레이어 구조

```
Component (Vue)
    ↓ (UI 로직)
Service Layer (TypeScript)
    ↓ (API 통신)
Backend API (FastAPI)
    ↓
AI Models (Gemini, Veo3)
```

### 코드 스타일

#### 1. Composition API 필수

```typescript
// ✅ 올바름 - <script setup> 사용
<script setup lang="ts">
import { ref, computed } from 'vue';

const count = ref(0);
const doubled = computed(() => count.value * 2);
</script>

// ❌ 잘못됨 - Options API
<script>
export default {
  data() { return { count: 0 }; }
}
</script>
```

#### 2. TypeScript 타입 정의 필수

```typescript
// ✅ 올바름 - 명확한 타입 정의
interface ImageProcessRequest {
  prompt: string;
  imageFile: File;
  options?: ProcessOptions;
}

async function processImage(request: ImageProcessRequest): Promise<string> {
  // ...
}

// ❌ 잘못됨 - 타입 없음
async function processImage(prompt, imageFile) {
  // ...
}
```

#### 3. shadcn-vue 컴포넌트 사용

```vue
<!-- ✅ 올바름 - shadcn-vue 컴포넌트 임포트 -->
<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
</script>

<template>
  <Card>
    <CardHeader>제목</CardHeader>
    <CardContent>
      <Button>클릭</Button>
    </CardContent>
  </Card>
</template>

<!-- ❌ 잘못됨 - components/ui/ 파일 직접 수정 -->
```

**주의**: `components/ui/` 폴더의 파일들은 shadcn-vue CLI로 생성되므로 직접 수정하지 마세요. 커스터마이징이 필요하면 새 컴포넌트를 만들어 래핑하세요.

#### 4. 명명 규칙

- **Components**: PascalCase (`FurnitureRemoval.vue`)
- **Services**: camelCase (`gemini.service.ts`)
- **Types**: PascalCase + Interface/Type 접두사 (`ImageProcessRequest`)
- **Utils**: camelCase (`generatePromptForStructure`)
- **Routes**: kebab-case (`/furniture-removal`)

### WebSocket 통신

장시간 실행되는 AI 작업(비디오 생성 등)은 WebSocket을 사용합니다:

```typescript
// services/bangkku/veo3.service.ts
class Veo3Service {
  async generateVideo(
    request: VideoGenerationRequest,
    callbacks: {
      onProgress?: (percent: number, message: string) => void;
      onCompleted?: (result: VideoResult) => void;
      onError?: (error: string) => void;
    }
  ): Promise<void> {
    const ws = new WebSocket('ws://localhost:8000/api/bangkku/ws/generate-video');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'progress':
          callbacks.onProgress?.(data.percent, data.message);
          break;
        case 'completed':
          callbacks.onCompleted?.(data.result);
          ws.close();
          break;
        case 'error':
          callbacks.onError?.(data.error);
          ws.close();
          break;
      }
    };
  }
}
```

### 에러 핸들링

모든 async 작업은 try-catch로 감싸야 합니다:

```typescript
// ✅ 올바름
try {
  const result = await geminiService.processImage(prompt, file);
  return result;
} catch (error) {
  console.error('Image processing failed:', error);
  showError('이미지 처리 중 오류가 발생했습니다.');
}

// ❌ 잘못됨
const result = await geminiService.processImage(prompt, file);
return result;
```

---

## 🎨 스타일 및 테마

### Tailwind CSS 4.x

프로젝트는 Tailwind CSS 4.x의 인라인 `@theme` 설정을 사용합니다:

```css
/* style.css */
@theme inline {
  --font-sans: "Pretendard Variable", Pretendard, ...;
  --radius-sm: calc(var(--radius) - 4px);
  /* ... */
}
```

### 다크 모드

다크 모드는 `.dark` 클래스로 토글됩니다:

```css
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  /* ... */
}
```

### 커스텀 CSS 변수

Tailwind의 색상 시스템은 CSS 변수로 관리됩니다:

```css
--color-primary: var(--primary);
--color-secondary: var(--secondary);
--color-muted: var(--muted);
/* ... */
```

---

## 🧪 주요 기능 상세

### 1. 가구 제거 (FurnitureRemoval.vue)

- **배치 처리**: 최대 10개 이미지 동시 처리
- **Drag & Drop**: 이미지 드래그 앤 드롭 지원
- **AI 프롬프트 편집**: Collapsible 프롬프트 에디터
- **기본 이미지**: 테스트용 기본 이미지 1개 제공

### 2. 가구 정면 샷 변환 (FurnitureFrontView.vue)

- **단일 이미지 처리**: 한 번에 1개 이미지 변환
- **실시간 미리보기**: 원본/결과 비교 뷰
- **재시도 기능**: 실패 시 재시도 버튼

### 3. 3D 룸 생성 (Room3DGenerator.vue)

- **구조 선택**: ㅡ자형(1면), ㄱ자형(2면), ㄷ자형(3면)
- **동적 프롬프트**: 선택한 구조에 따라 프롬프트 자동 생성
- **조건부 이미지 슬롯**: 구조에 맞는 이미지 업로드 슬롯만 표시
- **기본 이미지**: 각 구조별 기본 이미지 세트 제공

### 4. 비디오 생성 (VideoGenerator.vue)

- **WebSocket 통신**: 실시간 진행률 업데이트
- **진행률 표시**: 퍼센트 및 상태 메시지
- **Veo3.1 통합**: Google Veo3 AI 모델 사용

---

## 🔧 트러블슈팅

### 빌드 오류

```bash
# 캐시 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### 포트 충돌

Vite 기본 포트(12345)가 사용 중일 경우, `vite.config.ts`에서 포트 변경:

```typescript
export default defineConfig({
  server: {
    port: 3000, // 원하는 포트로 변경
  }
})
```

### API 키 오류

`.env` 파일에 올바른 Google Gemini API 키가 설정되어 있는지 확인:

```bash
VITE_GEMINI_API_KEY=your_actual_api_key_here
```

환경 변수는 `import.meta.env.VITE_*` 형식으로 접근:

```typescript
const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
```

### TypeScript 오류

```bash
# TypeScript 컴파일 체크
npm run build

# 타입 선언 파일 확인
npx vue-tsc --noEmit
```

---

### 외부 문서

- [Vue 3 공식 문서](https://vuejs.org/)
- [Vue Router 4](https://router.vuejs.org/)
- [shadcn-vue](https://www.shadcn-vue.com/)
- [Tailwind CSS 4](https://tailwindcss.com/)
- [Vite](https://vite.dev/)
- [TypeScript](https://www.typescriptlang.org/)
- [Google Gemini API](https://ai.google.dev/docs)

---

## 📝 라이선스

Copyright © 2025 새움소프트. All rights reserved.

---
