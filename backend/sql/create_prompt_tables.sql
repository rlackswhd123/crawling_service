-- =====================================================
-- AI 프롬프트 관리 테이블 생성 스크립트
-- =====================================================
-- Target DB: anytalk.com:5435 (postgres)
-- Created: 2025-01-28
-- Purpose: AI 프롬프트 버전 관리, 테스트 결과 추적, 성능 평가
-- =====================================================

-- =====================================================
-- 1. 시퀀스 생성
-- =====================================================

CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.member_seq START 1;
CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompts_seq START 1;
CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompt_test_results_seq START 1;
CREATE SEQUENCE IF NOT EXISTS saeum_ai_api.prompt_ratings_seq START 1;

-- =====================================================
-- 2. member 테이블 (사용자 정보)
-- =====================================================

CREATE TABLE IF NOT EXISTS saeum_ai_api.member (
    -- Primary Key
    user_key            bigint PRIMARY KEY DEFAULT nextval('saeum_ai_api.member_seq'),

    -- 사용자 정보
    user_name           character varying(100) NOT NULL,
    user_email          character varying(255),
    role_kind           character varying(20),             -- 'developer', 'operator'

    -- 감사 컬럼
    cre_date            timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    upd_date            timestamp with time zone,
    delete_yn           smallint DEFAULT 0
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_member_email ON saeum_ai_api.member(user_email);

-- 테이블 코멘트
COMMENT ON TABLE saeum_ai_api.member IS '사용자 정보 (개발자/운영자)';

-- 컬럼 코멘트
COMMENT ON COLUMN saeum_ai_api.member.user_key IS '사용자 고유 식별자 (PK)';
COMMENT ON COLUMN saeum_ai_api.member.user_name IS '사용자 이름';
COMMENT ON COLUMN saeum_ai_api.member.user_email IS '사용자 이메일 (선택적)';
COMMENT ON COLUMN saeum_ai_api.member.role_kind IS '역할 구분 (developer, operator 등)';
COMMENT ON COLUMN saeum_ai_api.member.cre_date IS '생성 일시';
COMMENT ON COLUMN saeum_ai_api.member.upd_date IS '수정 일시';
COMMENT ON COLUMN saeum_ai_api.member.delete_yn IS '삭제 여부 (0: 미삭제, 1: 삭제)';

-- =====================================================
-- 3. prompts 테이블 (프롬프트 메타데이터)
-- =====================================================

CREATE TABLE IF NOT EXISTS saeum_ai_api.prompts (
    -- Primary Key
    prompt_key          bigint PRIMARY KEY DEFAULT nextval('saeum_ai_api.prompts_seq'),

    -- 분류 (서비스/기능 통합 경로)
    prompt_kind         character varying(100) NOT NULL,  -- 'bangkku/furniture_removal'
    model_kind          character varying(50),             -- 'gemini', 'veo', 'gpt4'

    -- 프롬프트 내용
    prompt_text         text NOT NULL,

    -- 상태 및 통계
    is_default_yn       smallint DEFAULT 0,                -- prompt_kind별 디폴트 (0 or 1)
    use_cnt             integer DEFAULT 0,                 -- 사용 횟수
    success_cnt         integer DEFAULT 0,                 -- 성공 횟수
    avg_rating          numeric(3,2),                      -- 평균 평점 (1.00~5.00)

    -- 감사(Audit) 컬럼
    cre_date            timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    cre_user_key        bigint,
    upd_date            timestamp with time zone,
    upd_user_key        bigint,
    delete_yn           smallint DEFAULT 0
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_prompts_kind ON saeum_ai_api.prompts(prompt_kind);

-- UNIQUE 제약: prompt_kind별로 is_default_yn = 1은 하나만 허용
CREATE UNIQUE INDEX IF NOT EXISTS idx_prompts_default
    ON saeum_ai_api.prompts(prompt_kind)
    WHERE is_default_yn = 1 AND delete_yn = 0;

-- 테이블 코멘트
COMMENT ON TABLE saeum_ai_api.prompts IS 'AI 프롬프트 메타데이터 및 버전 관리';

-- 컬럼 코멘트
COMMENT ON COLUMN saeum_ai_api.prompts.prompt_key IS '프롬프트 고유 식별자 (PK)';
COMMENT ON COLUMN saeum_ai_api.prompts.prompt_kind IS '서비스/기능 경로 (예: bangkku/furniture_removal, anitalk/chat)';
COMMENT ON COLUMN saeum_ai_api.prompts.model_kind IS 'AI 모델 종류 (예: gemini, veo, gpt4, claude)';
COMMENT ON COLUMN saeum_ai_api.prompts.prompt_text IS '실제 프롬프트 본문 내용';
COMMENT ON COLUMN saeum_ai_api.prompts.is_default_yn IS 'prompt_kind별 디폴트 프롬프트 여부 (0: 일반, 1: 디폴트) - UNIQUE 제약';
COMMENT ON COLUMN saeum_ai_api.prompts.use_cnt IS '프롬프트 사용 횟수 (테스트 실행 횟수)';
COMMENT ON COLUMN saeum_ai_api.prompts.success_cnt IS '성공 실행 횟수 (success_yn = 1인 테스트 결과 수)';
COMMENT ON COLUMN saeum_ai_api.prompts.avg_rating IS '평균 평점 (1.00~5.00), prompt_ratings 테이블에서 자동 집계';
COMMENT ON COLUMN saeum_ai_api.prompts.cre_date IS '생성 일시';
COMMENT ON COLUMN saeum_ai_api.prompts.cre_user_key IS '생성자 사용자 키';
COMMENT ON COLUMN saeum_ai_api.prompts.upd_date IS '수정 일시';
COMMENT ON COLUMN saeum_ai_api.prompts.upd_user_key IS '수정자 사용자 키';
COMMENT ON COLUMN saeum_ai_api.prompts.delete_yn IS '삭제 여부 (0: 미삭제, 1: 삭제)';

-- =====================================================
-- 3. prompt_test_results 테이블 (테스트 결과 및 성능)
-- =====================================================

CREATE TABLE IF NOT EXISTS saeum_ai_api.prompt_test_results (
    -- Primary Key
    test_result_key     bigint PRIMARY KEY DEFAULT nextval('saeum_ai_api.prompt_test_results_seq'),

    -- Foreign Key
    prompt_key          bigint NOT NULL REFERENCES saeum_ai_api.prompts(prompt_key),

    -- 입력/출력 데이터
    input_params        jsonb,                             -- 입력 파라미터 (이미지 URL, 옵션 등)
    output_url          character varying(500),            -- 결과물 URL (이미지/영상)

    -- 성능 지표
    execution_time_ms   bigint,                            -- 실행 시간 (밀리초)
    token_cnt           integer,                           -- 사용 토큰 수
    cost_amount         numeric(10,4),                     -- 비용 (달러)

    -- 결과 상태
    success_yn          smallint NOT NULL,                 -- 성공(1)/실패(0)
    error_msg           text,                              -- 에러 메시지

    -- 감사 컬럼
    cre_date            timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    cre_user_key        bigint,
    delete_yn           smallint DEFAULT 0
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_test_results_prompt ON saeum_ai_api.prompt_test_results(prompt_key);
CREATE INDEX IF NOT EXISTS idx_test_results_date ON saeum_ai_api.prompt_test_results(cre_date DESC);
CREATE INDEX IF NOT EXISTS idx_test_results_success ON saeum_ai_api.prompt_test_results(success_yn);

-- 테이블 코멘트
COMMENT ON TABLE saeum_ai_api.prompt_test_results IS 'AI 프롬프트 테스트 실행 결과 및 성능 지표';

-- 컬럼 코멘트
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.test_result_key IS '테스트 결과 고유 식별자 (PK)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.prompt_key IS '사용된 프롬프트 FK (prompts.prompt_key)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.input_params IS 'JSON 형식 입력 파라미터 (예: {"image_url": "...", "options": {...}})';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.output_url IS '생성된 결과물 URL (이미지/비디오 등)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.execution_time_ms IS 'AI API 실행 시간 (밀리초 단위)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.token_cnt IS 'AI API 사용 토큰 수 (입력+출력)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.cost_amount IS 'AI API 비용 (달러 단위, 최대 $9,999.9999)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.success_yn IS '실행 성공 여부 (0: 실패, 1: 성공)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.error_msg IS '실패 시 에러 메시지 (success_yn = 0인 경우)';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.cre_date IS '테스트 실행 일시';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.cre_user_key IS '테스트 실행자 사용자 키';
COMMENT ON COLUMN saeum_ai_api.prompt_test_results.delete_yn IS '삭제 여부 (0: 미삭제, 1: 삭제)';

-- =====================================================
-- 4. prompt_ratings 테이블 (프롬프트 평가)
-- =====================================================

CREATE TABLE IF NOT EXISTS saeum_ai_api.prompt_ratings (
    -- Primary Key
    rating_key          bigint PRIMARY KEY DEFAULT nextval('saeum_ai_api.prompt_ratings_seq'),

    -- Foreign Keys (둘 중 하나는 필수)
    prompt_key          bigint REFERENCES saeum_ai_api.prompts(prompt_key),
    test_result_key     bigint REFERENCES saeum_ai_api.prompt_test_results(test_result_key),

    -- 평가 정보
    rater_user_key      bigint NOT NULL,                   -- 평가자 ID
    rating_score        smallint NOT NULL CHECK (rating_score BETWEEN 1 AND 5),
    rating_cmt          text,                              -- 평가 코멘트

    -- 감사 컬럼
    cre_date            timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    cre_user_key        bigint,
    upd_date            timestamp with time zone,
    upd_user_key        bigint,
    delete_yn           smallint DEFAULT 0
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_ratings_prompt ON saeum_ai_api.prompt_ratings(prompt_key);
CREATE INDEX IF NOT EXISTS idx_ratings_test_result ON saeum_ai_api.prompt_ratings(test_result_key);
CREATE INDEX IF NOT EXISTS idx_ratings_user ON saeum_ai_api.prompt_ratings(rater_user_key);

-- 테이블 코멘트
COMMENT ON TABLE saeum_ai_api.prompt_ratings IS '개발자/운영자의 프롬프트 품질 평가';

-- 컬럼 코멘트
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.rating_key IS '평가 고유 식별자 (PK)';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.prompt_key IS '평가 대상 프롬프트 FK (프롬프트 전체 평가 시 사용)';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.test_result_key IS '평가 대상 테스트 결과 FK (특정 테스트 결과 평가 시 사용)';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.rater_user_key IS '평가자 사용자 키 (개발자 또는 운영자)';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.rating_score IS '평점 (1: 매우 나쁨 ~ 5: 매우 좋음)';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.rating_cmt IS '평가 코멘트 (자유 형식 텍스트)';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.cre_date IS '평가 일시';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.cre_user_key IS '평가 생성자 사용자 키';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.upd_date IS '평가 수정 일시';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.upd_user_key IS '평가 수정자 사용자 키';
COMMENT ON COLUMN saeum_ai_api.prompt_ratings.delete_yn IS '삭제 여부 (0: 미삭제, 1: 삭제)';

-- =====================================================
-- 완료
-- =====================================================
-- 생성된 객체:
--   - 시퀀스: 4개 (member_seq, prompts_seq, prompt_test_results_seq, prompt_ratings_seq)
--   - 테이블: 4개 (member, prompts, prompt_test_results, prompt_ratings)
--   - 인덱스: 9개 (member email, prompts kind/default, test_results FK/date/success, ratings FKs)
--   - 컬럼 코멘트: 39개 (모든 컬럼)
--
-- 주요 변경사항:
--   - member 테이블 추가 (user_key, user_name, user_email, role_kind)
--   - prompts: prompt_title, prompt_desc 삭제
--   - prompts: use_count → use_cnt, success_count → success_cnt
--   - prompt_test_results: sample_desc 삭제
--   - prompt_test_results: token_count → token_cnt, error_message → error_msg
--   - prompt_ratings: rating_criteria 삭제, rating_comment → rating_cmt
-- =====================================================
