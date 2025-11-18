-- Supabase DDL: notices 테이블 스키마 변경
-- OCR 서비스용 컬럼 추가

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

-- 인덱스 추가 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_notices_has_ocr ON notices(has_ocr);
CREATE INDEX IF NOT EXISTS idx_notices_has_image ON notices(has_image);
CREATE INDEX IF NOT EXISTS idx_notices_ocr_at ON notices(ocr_at);

-- 조회용 뷰 생성
CREATE OR REPLACE VIEW notices_display AS
SELECT
  id, source, post_id, title, url, posted_at, attachments,
  COALESCE(merged_text, content_text) AS display_text,
  has_image, has_table, has_ocr, ocr_engine, ocr_at
FROM notices;

-- 코멘트 추가
COMMENT ON COLUMN notices.content_html_raw IS '원본 HTML (보관용)';
COMMENT ON COLUMN notices.content_text IS '일반 텍스트 추출 결과';
COMMENT ON COLUMN notices.ocr_text IS 'OCR로 추출된 텍스트';
COMMENT ON COLUMN notices.ocr_blocks IS 'OCR 블록 정보 (JSONB)';
COMMENT ON COLUMN notices.merged_text IS 'content_text + OCR 병합 텍스트';
COMMENT ON COLUMN notices.has_image IS '이미지 포함 여부';
COMMENT ON COLUMN notices.has_table IS '표 포함 여부';
COMMENT ON COLUMN notices.has_ocr IS 'OCR 처리 여부';
COMMENT ON COLUMN notices.ocr_engine IS '사용된 OCR 엔진';
COMMENT ON COLUMN notices.ocr_duration_ms IS 'OCR 처리 시간 (ms)';
COMMENT ON COLUMN notices.ocr_at IS 'OCR 처리 시각';
COMMENT ON COLUMN notices.process_rule_ver IS '처리 규칙 버전';
COMMENT ON COLUMN notices.content_hash IS '콘텐츠 해시 (중복 체크용)';

-- 저장 규칙 예시 (크롤러에서 사용)
-- 
-- UPDATE notices SET
--   ocr_text = 'OCR 결과 텍스트',
--   ocr_blocks = '블록 JSON',
--   merged_text = content_text || E'\n\n[IMAGE_OCR]\n' || ocr_text,
--   has_ocr = true,
--   ocr_engine = 'paddle',
--   ocr_duration_ms = 1270,
--   ocr_at = NOW()
-- WHERE id = 'xxx';

