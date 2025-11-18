/**
 * Prompt Management Type Definitions
 * 프롬프트 관리 시스템의 타입 정의
 */

/**
 * 기본 데이터베이스 모델 필드
 */
export interface BaseDBModel {
  creDate?: string;  // ISO 8601 datetime string
  creUserKey?: number;
  updDate?: string;  // ISO 8601 datetime string
  updUserKey?: number;
  deleteYn: number;  // 0 or 1
}

/**
 * 프롬프트 메인 모델
 */
export interface Prompt extends BaseDBModel {
  promptKey: number;
  promptKind: string;  // e.g., "bangkku/furniture-removal"
  modelKind?: string;  // e.g., "gemini-2.5-flash"
  promptText: string;
  isDefaultYn: number;  // 0 or 1
  avgRating?: number;  // Average rating score
  inputImages?: string[];  // Array of image URLs
}

/**
 * 프롬프트 생성 요청
 */
export interface PromptCreate {
  promptKind: string;
  modelKind?: string;
  promptText: string;
  isDefaultYn?: number;  // default: 0
}

/**
 * 프롬프트 수정 요청 (부분 수정 가능)
 */
export interface PromptUpdate {
  promptKind?: string;
  modelKind?: string;
  promptText?: string;
  isDefaultYn?: number;
}

/**
 * 프롬프트 테스트 결과
 */
export interface PromptTestResult extends BaseDBModel {
  testResultKey: number;
  promptKey: number;
  testCaseId: string;
  inputData: string;  // JSON string
  outputData: string;  // JSON string
  successYn: number;  // 0 or 1
  errorMessage?: string;
  executionTimeMs?: number;
  tokenUsage?: number;
  costEstimate?: number;
}

/**
 * 프롬프트 평가 생성 요청
 */
export interface PromptRatingCreate {
  promptKey?: number;
  testResultKey?: number;
  raterUserKey: number;
  ratingScore: number;  // 1-5
  ratingCmt?: string;
}

/**
 * 프롬프트 평가 (사용자 피드백)
 */
export interface PromptRating extends BaseDBModel {
  ratingKey: number;
  promptKey?: number;
  testResultKey?: number;
  raterUserKey: number;
  ratingScore: number;  // 1-5
  ratingCmt?: string;
}

/**
 * 평균 평점 통계
 */
export interface RatingStatistics {
  avgRating: number;
  totalRatings: number;
  ratingDistribution: {
    '1': number;
    '2': number;
    '3': number;
    '4': number;
    '5': number;
  };
}

/**
 * 프롬프트 통계 응답
 */
export interface PromptStatistics {
  promptKey: number;
  totalTests: number;
  successCount: number;
  failureCount: number;
  avgExecutionTimeMs?: number;
  avgTokenUsage?: number;
  avgCostEstimate?: number;
  avgRating?: number;
  totalRatings: number;
}

/**
 * 프롬프트 성능 통계 응답
 */
export interface PromptPerformanceStats {
  totalTests: number;
  successCount: number;
  failureCount: number;
  avgExecutionTimeMs?: number;
  avgTokenUsage?: number;
  avgCostEstimate?: number;
}

/**
 * 프롬프트 목록 조회 옵션
 */
export interface PromptListOptions {
  promptKind?: string;  // Filter by service/feature path
  includeNonDefault?: boolean;  // default: true
}

/**
 * 테스트 결과 목록 조회 옵션
 */
export interface TestResultListOptions {
  limit?: number;  // default: 20, max: 100
}

/**
 * 특정 프롬프트의 테스트 결과 조회 옵션
 */
export interface PromptTestResultOptions {
  successOnly?: boolean;  // default: false
  limit?: number;  // default: 50, max: 100
}
