# 사이트 유형 및 셀렉터 자동 분석 통합 기능 개발 계획

## 📋 개요

PRD 문서(`PRD_사이트_유형_및_셀렉터_자동_분석_통합.md`)를 기반으로 사이트 유형 분석 및 셀렉터 자동 감지 기능을 구현합니다.

## 🎯 개발 우선순위

### Phase 1: 핵심 기능 (필수) ⭐⭐⭐

**목표**: 기본적인 사이트 분석 및 도메인 추가 기능 구현

1. **데이터베이스 스키마**
   - `domains` 테이블 생성 (PRD 6.1절)
   - 필수 필드: id, name, base_url, source, site_type, use_selenium, content_selector 등
   - 인덱스 생성 (source, is_deleted)

2. **통합 HTML 수집 서비스**
   - `src/core/html_fetcher.py` 구현
   - HTTP/Selenium 자동 선택 로직
   - `fetch_html(url, use_selenium=None)` 함수

3. **사이트 유형 분석 모듈**
   - `src/core/site_analyzer.py` 구현
   - HTML 비교 기반 분석 (방법 1)
   - 정적/동적 사이트 판별
   - 신뢰도 점수 계산

4. **본문 셀렉터 자동 감지 모듈**
   - `src/core/selector_detector.py` 구현
   - 시맨틱 태그 우선순위
   - 클래스명 패턴 매칭
   - 텍스트 길이 기반 필터링
   - 여러 후보 셀렉터 생성

5. **백엔드 API 구현**
   - `POST /api/analyze-site`: 통합 분석 API
   - `POST /api/validate-selector`: 셀렉터 검증 API
   - `POST /api/crawling/domains`: 도메인 추가 API

6. **프론트엔드 API 연동**
   - `DomainCreateModal.vue`에서 Mock 데이터 제거
   - 실제 API 호출로 교체
   - 에러 처리 추가

### Phase 2: 고급 기능 (중요) ⭐⭐

**목표**: 사용자 경험 개선 및 안정성 향상

1. **분석 결과 DB 저장 및 캐싱**
   - 동일 도메인 재분석 시 저장된 결과 우선 사용
   - `forceReanalyze` 플래그 지원
   - `analyzed_at` 필드 업데이트

2. **에러 처리 및 폴백 로직**
   - 네트워크 에러 처리
   - 분석 실패 시 기본값 제공
   - 타임아웃 처리
   - 수동 입력 모드 전환

3. **검증 기능 강화**
   - 여러 URL 동시 검증
   - 검증 결과 상세 표시
   - 검증 통계 제공

4. **UI/UX 개선**
   - 로딩 상태 개선
   - 진행률 표시
   - 에러 메시지 개선
   - 미리보기 기능 강화

### Phase 3: 선택 기능 (향후) ⭐

**목표**: 고급 분석 기능 및 최적화

1. **JavaScript 의존성 탐지** (방법 2)
   - React, Vue, Angular 프레임워크 감지
   - 빈 컨테이너 확인
   - AJAX/fetch 호출 패턴 분석

2. **목록 셀렉터 자동 감지**
   - 게시글 목록 추출용 셀렉터 감지
   - 목록 구조 분석

3. **배치 분석 기능**
   - 여러 도메인 한 번에 분석
   - 분석 작업 큐 관리

4. **머신러닝 기반 셀렉터 추천**
   - 학습된 패턴 기반 추천
   - 도메인별 패턴 학습

## 📁 파일 구조

### 백엔드 (crawling_service)

```
susoft_service/crawling_service/
├── src/
│   ├── core/
│   │   ├── html_fetcher.py      # 통합 HTML 수집 (신규)
│   │   ├── site_analyzer.py     # 사이트 유형 분석 (신규)
│   │   └── selector_detector.py # 셀렉터 자동 감지 (신규)
│   ├── api/                     # API 라우터 (신규 또는 기존 확장)
│   │   └── analyze_router.py
│   └── storage/
│       └── domain_repo.py       # 도메인 저장소 (신규)
├── docs/
│   └── domains-schema.sql       # domains 테이블 스키마 (신규)
└── requirements.txt
```

### 프론트엔드

```
frontend/src/
├── components/crawling/
│   └── DomainCreateModal.vue   # 기존 파일 수정
├── services/crawling/
│   └── analyze.service.ts       # 분석 API 서비스 (신규)
└── types/
    └── crawling.types.ts        # 기존 파일 (타입 추가)
```

## 🔧 기술 스택

### 백엔드
- Python 3.8+
- FastAPI (또는 기존 프레임워크)
- BeautifulSoup4 (HTML 파싱)
- Selenium (동적 사이트)
- Supabase (데이터베이스)

### 프론트엔드
- Vue 3
- TypeScript
- 기존 UI 컴포넌트 활용

## 📝 상세 구현 계획

### 1. 데이터베이스 스키마

**파일**: `susoft_service/crawling_service/docs/domains-schema.sql`

PRD 6.1절의 스키마를 그대로 구현:
- `domains` 테이블 생성
- 필수 필드 및 인덱스
- `source` 자동 생성 규칙 적용

### 2. 통합 HTML 수집 서비스

**파일**: `susoft_service/crawling_service/src/core/html_fetcher.py`

```python
def fetch_html(url: str, use_selenium: Optional[bool] = None) -> str:
    """
    통합 HTML 수집 함수
    
    Args:
        url: 수집할 URL
        use_selenium: None이면 자동 판별, True/False면 강제 지정
    
    Returns:
        HTML 문자열
    """
    if use_selenium is None:
        # 사이트 유형 자동 판별 (간단한 휴리스틱)
        use_selenium = _should_use_selenium(url)
    
    if use_selenium:
        return _fetch_with_selenium(url)
    else:
        return _fetch_with_http(url)
```

### 3. 사이트 유형 분석

**파일**: `susoft_service/crawling_service/src/core/site_analyzer.py`

주요 함수:
- `analyze_site_type(base_url, list_url=None)`: 사이트 유형 분석
- `compare_html(http_html, selenium_html)`: HTML 비교
- `calculate_confidence(diff_ratio)`: 신뢰도 계산

분석 방법:
1. HTTP로 HTML 수집
2. Selenium으로 동일 페이지 렌더링 후 HTML 수집
3. DOM 요소 개수, 텍스트 길이 비교
4. 차이 임계값 기준 판단 (요소 수 차이 > 30%, 텍스트 길이 차이 > 50%)

### 4. 본문 셀렉터 자동 감지

**파일**: `susoft_service/crawling_service/src/core/selector_detector.py`

주요 함수:
- `detect_content_selector(url, base_url)`: 본문 셀렉터 감지
- `generate_candidates(html)`: 셀렉터 후보 생성
- `calculate_confidence(selector, html)`: 신뢰도 계산

알고리즘:
1. 시맨틱 태그 우선순위: `article`, `main`, `section`
2. 클래스명 패턴 매칭: `content`, `post`, `article`, `body`, `main`
3. 텍스트 길이 기반 필터링
4. 노이즈 요소 제거: `aside`, `nav`, `footer`, `header`, `script`, `style`

### 5. 백엔드 API

**엔드포인트**:
- `POST /api/analyze-site`: 통합 분석
- `POST /api/validate-selector`: 셀렉터 검증
- `POST /api/crawling/domains`: 도메인 추가

**요청/응답 형식**: PRD 4절 참조

### 6. 프론트엔드 연동

**수정 파일**: `frontend/src/components/crawling/DomainCreateModal.vue`

변경 사항:
- Mock 데이터 제거
- 실제 API 호출로 교체
- 에러 처리 추가
- 로딩 상태 개선

## 🚀 개발 순서

1. **데이터베이스 스키마 생성** (1일)
   - domains 테이블 생성
   - 마이그레이션 스크립트 작성

2. **통합 HTML 수집 서비스** (1일)
   - html_fetcher.py 구현
   - 기존 fetcher.py, selenium_fetcher.py 활용

3. **사이트 유형 분석 모듈** (2일)
   - site_analyzer.py 구현
   - HTML 비교 로직
   - 테스트 및 검증

4. **본문 셀렉터 감지 모듈** (3일)
   - selector_detector.py 구현
   - 셀렉터 후보 생성 알고리즘
   - 신뢰도 계산 로직

5. **백엔드 API 구현** (2일)
   - API 라우터 생성
   - 도메인 저장소 구현
   - 에러 처리

6. **프론트엔드 연동** (2일)
   - API 서비스 생성
   - DomainCreateModal 수정
   - 에러 처리 및 UI 개선

7. **테스트 및 버그 수정** (2일)
   - 통합 테스트
   - 버그 수정
   - 성능 최적화

**총 예상 기간**: 약 13일

## ✅ 체크리스트

### Phase 1 (필수)
- [ ] domains 테이블 생성
- [ ] 통합 HTML 수집 서비스 구현
- [ ] 사이트 유형 분석 모듈 구현
- [ ] 본문 셀렉터 자동 감지 모듈 구현
- [ ] 통합 분석 API 구현
- [ ] 셀렉터 검증 API 구현
- [ ] 도메인 추가 API 구현
- [ ] 프론트엔드 API 연동
- [ ] 분석 결과 DB 저장
- [ ] 기본 에러 처리

### Phase 2 (중요)
- [ ] 결과 캐싱 및 재사용
- [ ] 고급 에러 처리
- [ ] 검증 기능 강화
- [ ] UI/UX 개선

### Phase 3 (선택)
- [ ] JavaScript 의존성 탐지
- [ ] 목록 셀렉터 자동 감지
- [ ] 배치 분석 기능
- [ ] 머신러닝 기반 추천

## 📚 참고 자료

- PRD 문서: `susoft_service/PRD_사이트_유형_및_셀렉터_자동_분석_통합.md`
- 기존 코드:
  - `susoft_service/crawling_service/src/core/fetcher.py`
  - `susoft_service/crawling_service/src/core/selenium_fetcher.py`
  - `frontend/src/components/crawling/DomainCreateModal.vue`

