좋아! PRD에 **“MVP/일반 운영: 크롤러가 저장”** 원칙을 반영한 버전을 아래처럼 보강했어. (OCR 서비스는 **무상태·계산 전용**, Supabase **쓰기 권한은 크롤러만**)

---

# PRD (간단): 조건부 OCR 서비스 + Supabase 연동

## 0) 저장 책임(중요 원칙)

* **MVP/일반 운영: *크롤러가 저장* ✅**

  * OCR 서비스는 `full_text`/`blocks`만 **응답**하는 **무상태(stateless)** 서비스.
  * Supabase(Postgres) **쓰기/업데이트는 크롤러**가 수행한다(보안·일관성·중복방지).
  * `idempotency_key`(예: `source+post_id+file_hash`)로 **중복 호출/저장을 제어**한다.
* (확장 옵션) 대량 처리 시 **콜백/폴링/큐** 방식으로도 여전히 저장은 크롤러/워커가 담당.

---

## 1) 목적

* 크롤러가 **본문에 이미지/표 있을 때만** OCR API 호출 → 텍스트 추출.
* 결과는 Supabase의 **`ocr_text`** 로 저장, 조회용 **`merged_text`** 생성(`content_text` + OCR 결과).
* **MVP는 LayoutParser 없이** 시작(로그로 필요성 입증 후 플래그 온보드).

---

## 2) 범위 (In / Out)

**In**

* FastAPI 기반 **OCR 마이크로서비스** (동기 `/ocr/extract`)
* 파일 업로드/URL 입력, 엔진 선택(`paddle`/`gcv`)
* 블록 정규화(`blocks`) 및 병합 텍스트(`full_text`) **응답**
* Supabase 테이블 **컬럼 추가 & 저장 규칙**(저장은 크롤러)
* Swagger(`/docs`)로 스모크 테스트

**Out**

* 크롤러 본체(별도 서비스)
* 대시보드/UI, 비동기 잡 큐(차후)

---

## 3) 기술 스택

* **API**: FastAPI, Uvicorn
* **OCR 엔진**:

  * MVP: **PaddleOCR** (`use_angle_cls=True`, `lang="korean"`/`"korean_english"`)
  * 옵션: Google Vision / Document AI
* **이미지 처리**: Pillow(or OpenCV 최소)
* **DB**: Supabase(Postgres) + psycopg / supabase-py（**쓰기 주체는 크롤러**）
---

## 4) Supabase 스키마 변경 (DDL)

```sql
ALTER TABLE notices
  ADD COLUMN IF NOT EXISTS content_html_raw  TEXT NULL,
  ADD COLUMN IF NOT EXISTS content_text      TEXT NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS ocr_text          TEXT NULL,
  ADD COLUMN IF NOT EXISTS ocr_blocks        JSONB NULL,
  ADD COLUMN IF NOT EXISTS merged_text       TEXT NULL,
  ADD COLUMN IF NOT EXISTS has_image         BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS has_table         BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS has_ocr           BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS ocr_engine        TEXT NULL,
  ADD COLUMN IF NOT EXISTS ocr_duration_ms   INTEGER NULL,
  ADD COLUMN IF NOT EXISTS ocr_at            TIMESTAMPTZ NULL,
  ADD COLUMN IF NOT EXISTS process_rule_ver  TEXT NOT NULL DEFAULT 'v1.0',
  ADD COLUMN IF NOT EXISTS content_hash      TEXT NULL;

CREATE OR REPLACE VIEW notices_display AS
SELECT
  id, source, post_id, title, url, posted_at, attachments,
  COALESCE(merged_text, content_text) AS display_text,
  has_image, has_table, has_ocr, ocr_engine, ocr_at
FROM notices;
```

**저장 규칙(크롤러)**

* `ocr_text`가 NULL/빈값 → `merged_text := content_text`
* `ocr_text`가 존재 → `merged_text := content_text || E'\n\n[IMAGE_OCR]\n' || ocr_text`
* `has_ocr=true`, `ocr_engine`, `ocr_duration_ms`, `ocr_at` 갱신

---

## 5) API 설계

### 5.1 엔드포인트

* `POST /ocr/extract` — **동기 단건**(MVP, 무상태)

### 5.2 요청(`multipart/form-data` 또는 JSON)

* Fields:

  * `engine`: `"paddle" | "gcv"` (기본 `"paddle"`)
  * `use_layout`: `false|true` (기본 `false`, MVP)
  * `idempotency_key`: 필수(중복 제어용)
  * `file` 또는 `file_url` (택1)
* Header: `Authorization: Bearer <token>`

### 5.3 응답(정규화; 저장은 크롤러)

```json
{
  "engine": "paddle",
  "full_text": "OCR 병합 텍스트",
  "blocks": [
    {"type":"paragraph","text":"...","bbox":[x1,y1,x2,y2],"page":1}
  ],
  "meta": {"duration_ms": 1270, "pages": 1},
  "idempotency_key": "nsulib_2024_12345_abcd"
}
```

---

## 6) 처리 플로우

1. 입력 검증 → 2) **idempotency 캐시** → 3) (URL) 다운로드 → 4) 파이프라인

* `engine="paddle"`, `use_layout=false`(기본): PaddleOCR → 경량 후처리(y→x 정렬/소형박스 제거)
* `engine="paddle"`, `use_layout=true`(옵션): LayoutParser → 정렬/필터 → OCR
* `engine="gcv"`: Vision/DocAI → 블록 정규화

5. **full_text/blocks 반환(저장은 크롤러)** → 6) 구조화 로그·메트릭·캐시

---

## 7) 크롤러 측 조건부 호출 가이드

* 본문에 `<img>`/`<table>` 존재 → 후보
* 첨부 확장자/MIME `pdf|png|jpg|jpeg|tif` → 후보
* (선택 프리체크) 해상도/용량 하한 + 초경량 텍스트검출

---

## 8) FastAPI Swagger 테스트

* `/docs` → `POST /ocr/extract` → **Try it out**

  * `engine=paddle`, `use_layout=false`
  * `idempotency_key` 입력, `file` 업로드
* 응답 `full_text`/`meta` 확인 → 같은 키 재호출 시 캐시 hit

---

## 9) 구성(ENV)

```
OCR_ENGINE=paddle
USE_LAYOUT=false
GCP_PROJECT=...
GCP_CREDENTIALS_JSON=/secrets/gcp.json
REDIS_URL=redis://redis:6379
MAX_FILE_MB=20
AUTH_TOKEN=SECRET
DATABASE_URL=postgresql://...  # ← 실제 쓰기는 크롤러에서만 사용
```

---

## 10) 수용 기준(AC)

* `/docs` 업로드 시 **≤ 2s/페이지** 응답(MVP)
* 동일 `idempotency_key` 재호출 시 **<50ms** 캐시 응답
* **크롤러 저장 동작 확인**:

  * OCR 없음 → `merged_text == content_text`
  * OCR 있음 → `merged_text`에 `[IMAGE_OCR]` 섹션 포함
* `notices_display.display_text`로 일관 조회

---

### 한 줄 결론

* **OCR 서비스는 무상태 계산 전용, DB 저장은 크롤러가 담당(보안/일관성/중복제어 최적)**.
* MVP는 LayoutParser 없이 가볍게 시작하고, 로그로 필요성 확인 후 플래그로 점진 도입.
