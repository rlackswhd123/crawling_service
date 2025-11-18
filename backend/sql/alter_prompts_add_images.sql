-- 프롬프트 테이블에 입력 이미지 URL 컬럼 추가
-- 생성일: 2025-01-28

-- input_images 컬럼 추가 (JSONB 타입으로 여러 이미지 URL 저장)
ALTER TABLE saeum_ai_api.prompts
ADD COLUMN IF NOT EXISTS input_images JSONB DEFAULT '[]'::jsonb;

-- 컬럼 설명 추가
COMMENT ON COLUMN saeum_ai_api.prompts.input_images IS '프롬프트 입력 이미지 URL 배열 (예: ["/static/prompts/images/abc123.jpg", ...])';

-- 인덱스 추가 (JSONB 검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_prompts_input_images
ON saeum_ai_api.prompts USING gin (input_images);
