# PRD: 크롤링 파라미터 설정 및 실행 기능

## 1. 개요

프론트엔드에서 사용자가 입력한 크롤링 설정과 선택된 도메인 정보를 백엔드로 전달하여, 크롤링 서비스를 동적으로 실행할 수 있는 기능을 구현합니다.

## 2. 목표

- 사용자가 선택한 도메인에 대해 크롤링 설정을 입력하고 실행
- 프론트엔드 설정을 크롤링 서비스 설정 형식으로 자동 변환
- 동적 설정 파일 생성 및 크롤링 서비스 실행
- 크롤링 결과를 실시간으로 반환

## 3. 기능 요구사항

### 3.1 프론트엔드 요구사항

#### 3.1.1 크롤링 시작 모달
- 선택된 도메인 정보 표시 (읽기 전용)
- 사용자 입력 필드:
  - 시작 페이지 (필수)
  - 끝 페이지 (자동 엔드 페이지 체크 시 비활성화)
  - 자동 엔드 페이지 (체크박스)
  - OCR 엔진 선택 (선택사항)
  - page_param 파라미터 이름 (비어있으면 자동 추출)

#### 3.1.2 API 호출
- `POST /api/crawling/start` 엔드포인트 호출
- 도메인 정보와 크롤링 설정 전달

### 3.2 백엔드 요구사항

#### 3.2.1 API 엔드포인트
- **POST** `/api/crawling/start`
- 요청 데이터 수신 및 검증
- 도메인 정보 조회 (DB 또는 프론트엔드 전달 데이터)
- 크롤링 설정 변환 및 실행

#### 3.2.2 파라미터 변환
- 프론트엔드 설정 → 크롤링 서비스 설정 형식 변환
- 동적 설정 파일 생성 또는 메모리 기반 설정 객체 생성

#### 3.2.3 크롤링 서비스 실행
- 생성된 설정으로 크롤링 서비스 실행
- 결과 수집 및 반환

## 4. 데이터 구조

### 4.1 프론트엔드 → 백엔드 요청

```json
{
  "domainId": "550e8400-e29b-41d4-a716-446655440000",  // UUID 형식
  "domain": {
    "id": "550e8400-e29b-41d4-a716-446655440000",  // UUID
    "name": "제주도청",
    "baseUrl": "https://www.jeju.go.kr",
    "source": "jeju_go_kr",  // 크롤링 식별자
    "useSelenium": false,
    "contentSelector": "div.content > p",
    "siteType": "static",
    "siteTypeConfidence": 95
  },
  "config": {
    "startPage": 1,
    "endPage": 10,
    "autoEndPage": false,
    "ocrEngine": "paddle",
    "pageParam": "pageIndex"
  }
}
```

### 4.2 백엔드 → 크롤링 서비스 설정 변환

**변환 매핑 테이블**:

| 프론트엔드/DB 필드 | 크롤링 서비스 설정 필드 | 변환 규칙 |
|------------------|---------------------|----------|
| `domain.source` | `sites[].id` | 직접 매핑 (크롤링 식별자) |
| `domain.baseUrl` | `sites[].base_url` | 직접 매핑 |
| `domain.useSelenium` | `sites[].use_selenium` | 직접 매핑 |
| `domain.contentSelector` | `sites[].content_selector` | 직접 매핑 (향후 사용) |
| `config.startPage` | `sites[].start_page` | 직접 매핑 |
| `config.endPage` | `sites[].end_page` | `autoEndPage=false`일 때만 매핑 |
| `config.autoEndPage` | `sites[].auto_detect_end_page` | 직접 매핑 |
| `config.pageParam` | `sites[].page_param` | 비어있으면 자동 추출 또는 `None` |
| `config.ocrEngine` | `sites[].ocr_engine` | 직접 매핑 (향후 OCR 기능 연동) |

### 4.3 생성되는 설정 파일 구조

```yaml
sites:
  - id: jeju_go_kr  # domains.source 값 사용 (크롤링 식별자)
    enabled: true
    base_url: "https://www.jeju.go.kr"
    start_page: 1
    end_page: 10  # auto_detect_end_page가 false일 때만
    page_param: "pageIndex"  # 자동 추출 또는 사용자 입력
    fetch_detail: true  # 항상 true
    use_selenium: false
    content_selector: "div.content > p"  # 향후 사용
    auto_detect_end_page: false
    ocr_engine: "paddle"  # 향후 사용

http:
  user_agent: "Mozilla/5.0..."
  timeout: 30
  max_retries: 3
  retry_delay: 2

storage:
  use_supabase: true
  save_local_json: false  # API 호출 시에는 false 권장

logging:
  level: "INFO"
  format: "[%(asctime)s] %(levelname)s - %(message)s"
  file: null
```

## 5. 구현 방법

### 5.1 백엔드 API 구현

#### 5.1.1 엔드포인트 구조
- **POST** `/api/crawling/start`
- 요청 데이터 검증
- 도메인 정보 조회 (DB 또는 프론트엔드 데이터 사용)
- 설정 변환 및 크롤링 실행

#### 5.1.2 응답 데이터
```json
{
  "success": true,
  "jobId": "crawl_123456",  // 작업 식별자 (선택사항)
  "message": "크롤링이 시작되었습니다",
  "stats": {
    "totalPages": 10,
    "totalPosts": 47,
    "successCount": 45,
    "failedCount": 2,
    "duration": 120.5
  }
}
```

### 5.2 파라미터 변환 로직

#### 5.2.1 도메인 정보 조회
1. `domainId` (UUID)로 `domains` 테이블에서 도메인 정보 조회
2. 조회된 도메인의 `source` 값 추출
3. DB 정보와 프론트엔드 전달 정보 병합
   - DB 정보 우선, 없으면 프론트엔드 정보 사용
4. 크롤링 실행 시 `domains.source` 값을 `notices.source`에 저장

#### 5.2.2 설정 변환
1. 프론트엔드 설정과 도메인 정보 결합
2. 크롤링 서비스 설정 형식으로 변환
   - `domains.source` 값을 `sites[].id`로 사용 (크롤링 식별자)
   - 크롤링 결과는 `notices.source`에 동일한 값 저장
   - 크롤링된 게시물의 `source` 필드에 `domains.source` 값 저장
3. 필수 필드 검증

#### 5.2.3 page_param 자동 추출
- `config.pageParam`이 비어있을 때:
  1. `domain.baseUrl`로 목록 페이지 HTML 수집
  2. 페이지네이션 링크 분석
     - `<a href="?page=2">`, `<a href="?pageIndex=2">` 등 패턴 찾기
  3. 가장 많이 사용된 파라미터 이름 반환
  4. 설정에 자동으로 채워넣기
- 추출 실패 시:
  - 기본값 사용 (`page`, `pageIndex`, `pn` 등 시도)
  - 또는 사용자에게 입력 요청

### 5.3 설정 파일 생성 방법

#### 방법 1: 임시 파일 생성 (권장)
- 임시 디렉토리에 YAML 파일 생성
- 크롤링 서비스 실행 후 파일 삭제
- 장점: 기존 CLI 구조 그대로 사용 가능
- 단점: 파일 I/O 오버헤드

#### 방법 2: 메모리 기반 설정 객체
- 설정 딕셔너리를 메모리에서 직접 생성
- 크롤링 로직을 직접 호출 (CLI 우회)
- 장점: 빠르고 효율적
- 단점: 기존 CLI 구조 수정 필요


### 5.4 크롤링 서비스 실행

#### 실행 방법 1: subprocess로 CLI 호출
- 기존 CLI 명령어를 subprocess로 실행
- 설정 파일 경로 전달
- 장점: 기존 구조 그대로 사용
- 단점: 프로세스 오버헤드

#### 실행 방법 2: Python 모듈 직접 import
- 크롤링 로직을 직접 import하여 실행
- CLI를 거치지 않고 함수 호출
- 장점: 빠르고 효율적
- 단점: 코드 구조 변경 필요

### 5.5 비동기 처리 (선택사항)

#### 옵션 1: 동기 실행
- API 요청 받으면 즉시 크롤링 실행
- 완료 후 결과 반환
- 장점: 구현 단순
- 단점: 긴 작업 시 타임아웃 가능


## 6. 에러 처리

### 6.1 검증 에러
- 필수 필드 누락
- 잘못된 페이지 번호 (음수, 0 등)
- 잘못된 도메인 ID (UUID 형식 검증)
- 존재하지 않는 도메인 ID

### 6.2 크롤링 에러
- 네트워크 연결 실패
- 타임아웃
- 파싱 실패
- 부분 실패 시 성공한 데이터는 저장

### 6.3 에러 응답 형식
```json
{
  "success": false,
  "error": "에러 메시지",
  "errorCode": "NETWORK_ERROR" | "PARSING_ERROR" | "VALIDATION_ERROR"
}
```

## 7. 성능 고려사항

### 7.1 동시 실행 제한
- 같은 도메인 동시 크롤링 방지
- 전체 크롤링 작업 수 제한
- 작업 큐 또는 락 메커니즘 사용

### 7.2 타임아웃 설정
- 전체 크롤링: 최대 30분
- 페이지당: 최대 2분
- 네트워크 요청: 최대 30초

### 7.3 리소스 관리
- Selenium 드라이버 풀 관리
- 메모리 사용량 모니터링
- 임시 파일 정리

## 8. 보안 고려사항

### 8.1 입력 검증
- URL 형식 검증
- SQL Injection 방지
- XSS 방지

### 8.2 리소스 제한
- 최대 페이지 수 제한
- 최대 크롤링 시간 제한
- 동시 실행 수 제한

## 9. 향후 개선사항

### 9.1 크롤링 히스토리
- 과거 크롤링 작업 목록 조회
- 작업별 결과 통계
- 재실행 기능

### 9.2 스케줄링
- 정기 크롤링 스케줄 설정
- 자동 실행 기능

### 9.3 알림 기능
- 크롤링 완료 알림
- 에러 발생 알림
- 이메일/슬랙 연동

## 10. 우선순위

### Phase 1 (필수)
- ✅ 프론트엔드 크롤링 시작 모달 (이미 구현 완료)
- ✅ 백엔드 API 엔드포인트
- ✅ 파라미터 변환 로직
- ✅ 동적 설정 파일 생성
- ✅ 크롤링 서비스 실행
- ✅ 기본 에러 처리

### Phase 2 (중요)
- ✅ page_param 자동 추출
- ✅ 동시 실행 제한
- ✅ 진행 상황 전송 (WebSocket/SSE)
- ✅ 상세 에러 처리



