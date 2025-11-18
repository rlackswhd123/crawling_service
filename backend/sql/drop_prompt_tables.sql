-- =====================================================
-- AI 프롬프트 관리 테이블 삭제 스크립트
-- =====================================================
-- Target DB: anytalk.com:5435 (postgres)
-- Created: 2025-01-28
-- Purpose: 기존 테이블 및 시퀀스 삭제
-- =====================================================

-- =====================================================
-- 1. 테이블 삭제 (외래키 관계 역순)
-- =====================================================

-- 자식 테이블부터 삭제
DROP TABLE IF EXISTS saeum_ai_api.prompt_ratings CASCADE;
DROP TABLE IF EXISTS saeum_ai_api.prompt_test_results CASCADE;

-- 부모 테이블 삭제
DROP TABLE IF EXISTS saeum_ai_api.prompts CASCADE;
DROP TABLE IF EXISTS saeum_ai_api.member CASCADE;

-- =====================================================
-- 2. 시퀀스 삭제
-- =====================================================

DROP SEQUENCE IF EXISTS saeum_ai_api.prompt_ratings_seq;
DROP SEQUENCE IF EXISTS saeum_ai_api.prompt_test_results_seq;
DROP SEQUENCE IF EXISTS saeum_ai_api.prompts_seq;
DROP SEQUENCE IF EXISTS saeum_ai_api.member_seq;

-- =====================================================
-- 완료
-- =====================================================
-- 삭제된 객체:
--   - 테이블: 4개 (prompt_ratings, prompt_test_results, prompts, member)
--   - 시퀀스: 4개 (prompt_ratings_seq, prompt_test_results_seq, prompts_seq, member_seq)
-- =====================================================
