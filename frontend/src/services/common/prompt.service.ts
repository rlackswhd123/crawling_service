/**
 * Prompt Management Service
 * 프롬프트 관리 API 클라이언트
 */

import type {
  Prompt,
  PromptCreate,
  PromptUpdate,
  PromptListOptions,
  PromptStatistics,
  PromptTestResult,
  TestResultListOptions,
  PromptTestResultOptions,
  PromptPerformanceStats,
  PromptRating,
  PromptRatingCreate,
  RatingStatistics,
} from '@/types/prompt.types';

// Backend API Base URL from environment
// const API_URL = import.meta.env.VITE_API_URL || 'localhost:12346';
// 항상 HTTPS 기반으로 고정
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:12346';
const BASE_URL = `${API_URL}`;

// const BASE_URL = `${API_URL}`;

/**
 * API Error Handler
 */
class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Generic API Request Handler
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
 

  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP Error ${response.status}`,
        response.status,
        errorData
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    console.error('API Request failed:', error);
    throw new Error(`Failed to fetch: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// ==================== Prompt Management APIs ====================

/**
 * 프롬프트 생성
 */
export async function createPrompt(data: PromptCreate): Promise<Prompt> {
  return apiRequest<Prompt>('/api/prompts/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 프롬프트 생성 (이미지 포함)
 */
export async function createPromptWithImages(data: {
  promptKind: string;
  promptText: string;
  isDefaultYn: number;
  modelKind?: string;
  imageFiles?: File[];
}): Promise<Prompt> {
  const formData = new FormData();

  // Add text fields
  formData.append('prompt_kind', data.promptKind);
  formData.append('prompt_text', data.promptText);
  formData.append('is_default_yn', String(data.isDefaultYn));

  if (data.modelKind) {
    formData.append('model_kind', data.modelKind);
  }

  // Add image files
  if (data.imageFiles && data.imageFiles.length > 0) {
    data.imageFiles.forEach((file) => {
      formData.append('images', file);
    });
  }

  const url = `${BASE_URL}/api/prompts/with-images`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP Error ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    console.error('Create prompt with images failed:', error);
    throw new Error(`Failed to create prompt: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * 프롬프트 조회 (단일)
 */
export async function getPrompt(promptKey: number): Promise<Prompt> {
  return apiRequest<Prompt>(`/api/prompts/${promptKey}`);
}

/**
 * 프롬프트 목록 조회
 */
export async function listPrompts(options?: PromptListOptions): Promise<Prompt[]> {
  const params = new URLSearchParams();

  if (options?.promptKind) {
    params.append('promptKind', options.promptKind);
  }
  if (options?.includeNonDefault !== undefined) {
    params.append('includeNonDefault', String(options.includeNonDefault));
  }

  const query = params.toString();
  const endpoint = query ? `/api/prompts/?${query}` : '/api/prompts/';

  return apiRequest<Prompt[]>(endpoint);
}

/**
 * 프롬프트 수정
 */
export async function updatePrompt(
  promptKey: number,
  data: PromptUpdate
): Promise<Prompt> {
  return apiRequest<Prompt>(`/api/prompts/${promptKey}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * 프롬프트 삭제 (Soft Delete)
 */
export async function deletePrompt(promptKey: number): Promise<void> {
  return apiRequest<void>(`/api/prompts/${promptKey}`, {
    method: 'DELETE',
  });
}

/**
 * 기본 프롬프트로 설정
 */
export async function setAsDefaultPrompt(promptKey: number): Promise<Prompt> {
  return apiRequest<Prompt>(`/api/prompts/${promptKey}/set-default`, {
    method: 'POST',
  });
}

/**
 * 프롬프트 통계 조회
 */
export async function getPromptStatistics(promptKey: number): Promise<PromptStatistics> {
  return apiRequest<PromptStatistics>(`/api/prompts/${promptKey}/statistics`);
}

// ==================== Test Result Management APIs ====================

/**
 * 최근 테스트 결과 조회 (전체 프롬프트)
 */
export async function getRecentTestResults(
  options?: TestResultListOptions
): Promise<PromptTestResult[]> {
  const params = new URLSearchParams();

  if (options?.limit) {
    params.append('limit', String(options.limit));
  }

  const query = params.toString();
  const endpoint = query ? `/api/test-results/recent?${query}` : '/api/test-results/recent';

  return apiRequest<PromptTestResult[]>(endpoint);
}

/**
 * 실패한 테스트 결과 조회 (디버깅용)
 */
export async function getFailureTestResults(
  options?: TestResultListOptions
): Promise<PromptTestResult[]> {
  const params = new URLSearchParams();

  if (options?.limit) {
    params.append('limit', String(options.limit));
  }

  const query = params.toString();
  const endpoint = query ? `/api/test-results/failures?${query}` : '/api/test-results/failures';

  return apiRequest<PromptTestResult[]>(endpoint);
}

/**
 * 특정 프롬프트의 테스트 결과 조회
 */
export async function getTestResultsByPrompt(
  promptKey: number,
  options?: PromptTestResultOptions
): Promise<PromptTestResult[]> {
  const params = new URLSearchParams();

  if (options?.successOnly !== undefined) {
    params.append('successOnly', String(options.successOnly));
  }
  if (options?.limit) {
    params.append('limit', String(options.limit));
  }

  const query = params.toString();
  const endpoint = query
    ? `/api/test-results/prompt/${promptKey}?${query}`
    : `/api/test-results/prompt/${promptKey}`;

  return apiRequest<PromptTestResult[]>(endpoint);
}

/**
 * 특정 테스트 결과 조회
 */
export async function getTestResult(testResultKey: number): Promise<PromptTestResult> {
  return apiRequest<PromptTestResult>(`/api/test-results/${testResultKey}`);
}

/**
 * 프롬프트 성능 통계 조회
 */
export async function getPromptPerformanceStats(
  promptKey: number
): Promise<PromptPerformanceStats> {
  return apiRequest<PromptPerformanceStats>(`/api/test-results/prompt/${promptKey}/performance`);
}

// ==================== Utility Functions ====================

/**
 * 프롬프트 종류로 기본 프롬프트 조회
 */
export async function getDefaultPrompt(promptKind: string): Promise<Prompt | null> {
  const prompts = await listPrompts({
    promptKind,
    includeNonDefault: false, // Only default prompts
  });

  return prompts.find((p) => p.isDefaultYn === 1) || null;
}

/**
 * 프롬프트 복제 (새 버전 생성)
 */
export async function clonePrompt(
  promptKey: number,
  overrides?: Partial<PromptCreate>
): Promise<Prompt> {
  const original = await getPrompt(promptKey);

  const newPrompt: PromptCreate = {
    promptKind: original.promptKind,
    modelKind: original.modelKind,
    promptText: original.promptText,
    isDefaultYn: 0, // New clone is not default
    ...overrides,
  };

  return createPrompt(newPrompt);
}

/**
 * 성공률 계산
 */
export function calculateSuccessRate(stats: PromptStatistics | PromptPerformanceStats): number {
  if (stats.totalTests === 0) return 0;
  return (stats.successCount / stats.totalTests) * 100;
}

// ==================== Rating Management APIs ====================

/**
 * 프롬프트 평가 생성
 */
export async function createRating(
  promptKey: number,
  data: PromptRatingCreate
): Promise<PromptRating> {
  return apiRequest<PromptRating>(`/api/prompts/${promptKey}/ratings`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * 특정 프롬프트의 평가 목록 조회
 */
export async function getRatingsByPrompt(
  promptKey: number,
  limit: number = 50
): Promise<PromptRating[]> {
  const params = new URLSearchParams();
  params.append('limit', String(limit));

  return apiRequest<PromptRating[]>(`/api/prompts/${promptKey}/ratings?${params.toString()}`);
}

/**
 * 특정 프롬프트의 평균 평점 및 통계 조회
 */
export async function getAverageRating(promptKey: number): Promise<RatingStatistics> {
  return apiRequest<RatingStatistics>(`/api/prompts/${promptKey}/ratings/average`);
}

/**
 * 프롬프트 평가 제출 (간편 함수)
 * raterUserKey는 자동으로 1로 설정 (인증 없음)
 */
export async function submitPromptRating(data: {
  promptKey: number;
  ratingScore: number;
  ratingCmt?: string;
}): Promise<PromptRating> {
  return createRating(data.promptKey, {
    ratingScore: data.ratingScore,
    ratingCmt: data.ratingCmt,
    raterUserKey: 1, // 임시 사용자 (인증 없음)
  });
}

/**
 * 프롬프트 평가 삭제
 */
export async function deleteRating(ratingKey: number): Promise<void> {
  return apiRequest<void>(`/api/ratings/${ratingKey}`, {
    method: 'DELETE',
  });
}
