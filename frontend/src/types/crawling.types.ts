// Crawling 관련 타입 정의

export interface Service {
  id: number | string;  // UUID 또는 숫자 ID
  name: string;  // 예: "공지사항", "자유게시판", "문의게시판"
  url: string;   // 해당 서비스의 URL
  contentSelector?: string;  // 본문 셀렉터
  attachmentSelector?: string;  // 첨부파일 셀렉터
}

export interface Domain {
  id: number | string;  // UUID 또는 숫자 ID
  name: string;
  baseUrl: string;
  source?: string;  // 도메인 source (크롤링 식별자)
  useSelenium: boolean;
  services?: Service[];  // 해당 도메인의 서비스 목록
}

export interface Post {
  id: string;
  post_id: string;  // 실제 사이트의 post_id
  title: string;
  url: string;
  postAt: string;
  content: string;
  selector: string;
  attachments: Attachment[];
}

export interface Attachment {
  name: string;
  size: string;
  url?: string;
}

export interface CrawlConfig {
  id: string;
  startPage: number;
  endPage: number;
  autoEndPage: boolean;
  ocrEngine: string;
  pageParam: string;
}

export interface SiteTypeResult {
  type: 'static' | 'dynamic';
  method: 'http' | 'selenium';
  confidence: number;
  analysisMethod?: string;
}

export interface SelectorCandidate {
  selector: string;
  confidence: number;
  extractedText: string;
  textLength: number;
}

export interface SelectorResult {
  selector: string;
  confidence: number;
  candidates: SelectorCandidate[];
}

export interface AnalyzeSiteResponse {
  siteType: SiteTypeResult;
  selectors: {
    content: SelectorResult;
  };
  status: 'success' | 'error';
  error?: string;
  analyzedAt?: string;
}

export interface ValidationResult {
  url: string;
  success: boolean;
  extractedText?: string;
  textLength?: number;
  error?: string;
}

