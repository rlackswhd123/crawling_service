/**
 * 크롤링 서비스 API
 */

import type { AnalyzeSiteResponse } from '@/types/crawling.types';

// 크롤링 서비스는 독립적인 서버로 실행됩니다
const API_BASE_URL = import.meta.env.VITE_CRAWLING_API_URL || 'http://localhost:8000';

/**
 * 본문 셀렉터 분석 API
 */
export async function analyzeContent(params: {
  url?: string;
  html?: string;
}): Promise<AnalyzeSiteResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze-content`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // API 응답을 프론트엔드 타입으로 변환
    return {
      siteType: {
        type: 'static',
        method: 'http',
        confidence: 100,
      },
      selectors: {
        content: {
          selector: data.selectors.content.selector || '',
          confidence: data.selectors.content.confidence || 0,
          candidates: data.selectors.content.candidates || [],
        },
      },
      status: data.success ? 'success' : 'error',
      error: data.error,
      analyzedAt: new Date().toISOString(),
    };
  } catch (error) {
    console.error('본문 분석 중 에러 발생:', error);
    throw error;
  }
}

/**
 * 크롤링 시작 API
 */
export async function startCrawl(params: {
  domain: any;
  service: any;
  config: any;
}): Promise<{
  success: boolean;
  message: string;
  stats?: any;
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('크롤링 시작 중 에러 발생:', error);
    throw error;
  }
}

/**
 * 셀렉터 테스트 API (수동 입력 셀렉터 미리보기용)
 */
export async function testSelector(params: {
  url: string;
  selector: string;
}): Promise<{
  success: boolean;
  extractedText?: string;
  textLength: number;
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/test-selector`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('셀렉터 테스트 중 에러 발생:', error);
    throw error;
  }
}

/**
 * 게시글 목록 조회 API (post_contents 테이블)
 */
export async function getPosts(params: {
  domainId?: string;
  serviceId?: string;
  limit?: number;
  offset?: number;
}): Promise<Array<{
  id: string;
  title: string;
  url: string;
  postAt?: string;
  content?: string;
  contentText?: string;
  crawledAt: string;
  attachments?: Array<{ name: string; url?: string; type?: string; size?: number }>;
}>> {
  try {
    const queryParams = new URLSearchParams();
    if (params.domainId) queryParams.append('domain_id', params.domainId);
    if (params.serviceId) queryParams.append('service_id', params.serviceId);
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());

    const response = await fetch(`${API_BASE_URL}/api/posts?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('게시글 목록 조회 중 에러 발생:', error);
    throw error;
  }
}

/**
 * 크롤링 서비스 상태 확인
 */
export async function checkCrawlingHealth(): Promise<{
  status: string;
  analyzer_available: boolean;
  fetcher_available: boolean;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('크롤링 서비스 상태 확인 실패:', error);
    throw error;
  }
}

