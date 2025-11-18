/**
 * 도메인 및 서비스 관리 API
 */

const API_BASE_URL = import.meta.env.VITE_CRAWLING_API_URL || 'http://localhost:8000';

export interface Domain {
  id: string;
  name: string;
  baseUrl: string;
  source: string;
  useSelenium: boolean;
  contentSelector?: string;
  attachmentSelector?: string;
}

export interface Service {
  id: string;
  domainId: string;
  name: string;
  url: string;
  contentSelector: string;
  attachmentSelector?: string;
}

/**
 * 도메인 목록 조회
 */
export async function getDomains(): Promise<Domain[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/domains`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('도메인 목록 조회 실패:', error);
    throw error;
  }
}

/**
 * 도메인 생성
 */
export async function createDomain(data: {
  name: string;
  baseUrl: string;
  useSelenium: boolean;
}): Promise<Domain> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/domains`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('도메인 생성 실패:', error);
    throw error;
  }
}

/**
 * 도메인 삭제
 */
export async function deleteDomain(domainId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/domains/${domainId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('도메인 삭제 실패:', error);
    throw error;
  }
}

/**
 * 서비스 목록 조회
 */
export async function getServices(domainId: string): Promise<Service[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/domains/${domainId}/services`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('서비스 목록 조회 실패:', error);
    throw error;
  }
}

/**
 * 서비스 생성
 */
export async function createService(data: {
  domainId: string;
  name: string;
  url: string;
  contentSelector: string;
  attachmentSelector?: string;
}): Promise<Service> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/services`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('서비스 생성 실패:', error);
    throw error;
  }
}

/**
 * 서비스 삭제
 */
export async function deleteService(serviceId: string): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/services/${serviceId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.error('서비스 삭제 실패:', error);
    throw error;
  }
}

