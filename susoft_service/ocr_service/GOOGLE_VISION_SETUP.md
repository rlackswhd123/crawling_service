# Google Cloud Vision API 추가 가이드

## 개요
현재 프로젝트는 PaddleOCR을 사용하고 있으며, Google Cloud Vision API를 추가하여 OCR 엔진을 선택할 수 있도록 확장할 수 있습니다.

## 1. 사전 준비사항

### 1.1 Google Cloud 프로젝트 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **Cloud Vision API** 활성화
   - API 및 서비스 > 라이브러리 > "Cloud Vision API" 검색 > 활성화

### 1.2 서비스 계정 키 생성
1. IAM 및 관리자 > 서비스 계정
2. 서비스 계정 생성 또는 기존 계정 선택
3. 역할: "Cloud Vision API 사용자" 부여
4. 키 생성 (JSON 형식) 후 다운로드

## 2. 환경 변수 설정

`.env` 파일에 다음 설정 추가:

```env
# Google Cloud 설정
GCP_PROJECT=your-project-id
GCP_CREDENTIALS_JSON=/path/to/service-account-key.json
```

또는 JSON 내용을 직접 설정:
```env
GCP_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}
```

## 3. 의존성 추가

`requirements.txt`에 추가:
```
google-cloud-vision==3.4.5
```

설치:
```bash
pip install google-cloud-vision==3.4.5
```

## 4. 구현 단계

### 4.1 Google Vision 엔진 클래스 생성
`app/ocr/google_vision_engine.py` 파일 생성

```python
"""Google Cloud Vision Engine Wrapper"""
import time
from typing import List, Tuple
from google.cloud import vision
from google.oauth2 import service_account
import json
from app.config import settings


class GoogleVisionEngine:
    """Google Cloud Vision OCR 엔진 래퍼"""
    
    def __init__(self):
        """Google Vision 클라이언트 초기화"""
        credentials = None
        
        if settings.gcp_credentials_json:
            # JSON 파일 경로 또는 JSON 문자열
            if settings.gcp_credentials_json.startswith('{'):
                # JSON 문자열인 경우
                creds_dict = json.loads(settings.gcp_credentials_json)
                credentials = service_account.Credentials.from_service_account_info(creds_dict)
            else:
                # 파일 경로인 경우
                credentials = service_account.Credentials.from_service_account_file(
                    settings.gcp_credentials_json
                )
        
        self.client = vision.ImageAnnotatorClient(credentials=credentials)
    
    def extract(self, image_path: str) -> Tuple[List[dict], int]:
        """
        이미지에서 텍스트 추출
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            (결과 리스트, 소요 시간(ms))
        """
        start_time = time.time()
        
        # 이미지 읽기
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        
        # OCR 실행
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 결과 정규화
        blocks = []
        if texts:
            # 첫 번째 요소는 전체 텍스트이므로 제외
            for text in texts[1:]:
                vertices = text.bounding_poly.vertices
                if len(vertices) >= 4:
                    # bbox를 [x1, y1, x2, y2] 형식으로 변환
                    x_coords = [v.x for v in vertices]
                    y_coords = [v.y for v in vertices]
                    
                    blocks.append({
                        "bbox": [
                            min(x_coords),
                            min(y_coords),
                            max(x_coords),
                            max(y_coords)
                        ],
                        "text": text.description,
                        "confidence": 1.0  # Google Vision은 confidence를 제공하지 않음
                    })
        
        return blocks, duration_ms
```

### 4.2 API 엔드포인트 수정
`app/api/ocr.py` 파일 수정:

1. Google Vision 엔진 import 추가:
```python
from app.ocr.google_vision_engine import GoogleVisionEngine
```

2. Google Vision 엔진 싱글톤 추가:
```python
_google_vision_engine: Optional[GoogleVisionEngine] = None

def get_google_vision_engine() -> GoogleVisionEngine:
    """Google Vision 엔진 싱글톤"""
    global _google_vision_engine
    if _google_vision_engine is None:
        _google_vision_engine = GoogleVisionEngine()
    return _google_vision_engine
```

3. `extract_ocr` 함수에서 GCV 처리 로직 추가:
```python
# 기존 코드 (108-112줄) 제거하고 아래로 교체
if engine == "gcv":
    if not settings.gcp_project or not settings.gcp_credentials_json:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Cloud Vision not configured. Set GCP_PROJECT and GCP_CREDENTIALS_JSON"
        )

# OCR 실행 부분 (150-164줄) 수정
if engine == "paddle":
    paddle_engine = get_paddle_engine()
    raw_blocks, ocr_duration_ms = paddle_engine.extract(tmp_file_path)
    
    # 블록 후처리
    raw_blocks = filter_small_boxes(raw_blocks)
    raw_blocks = sort_blocks_by_reading_order(raw_blocks)
    
    # 정규화
    normalized_blocks = normalize_blocks(raw_blocks, page=1)
    full_text = generate_full_text(normalized_blocks)

elif engine == "gcv":
    gcv_engine = get_google_vision_engine()
    raw_blocks, ocr_duration_ms = gcv_engine.extract(tmp_file_path)
    
    # 블록 후처리
    raw_blocks = filter_small_boxes(raw_blocks)
    raw_blocks = sort_blocks_by_reading_order(raw_blocks)
    
    # 정규화
    normalized_blocks = normalize_blocks(raw_blocks, page=1)
    full_text = generate_full_text(normalized_blocks)
```

## 5. 테스트

### 5.1 API 호출 예시
```bash
curl -X POST "http://localhost:8000/ocr/extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "idempotency_key=test-key-123" \
  -F "engine=gcv" \
  -F "file=@test_image.jpg"
```

### 5.2 URL 방식
```bash
curl -X POST "http://localhost:8000/ocr/extract" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "idempotency_key=test-key-456" \
  -F "engine=gcv" \
  -F "file_url=https://example.com/image.jpg"
```

## 6. 비용 고려사항

Google Cloud Vision API는 사용량 기반 과금:
- 첫 1,000건/월: 무료
- 이후: 이미지당 $1.50 (텍스트 감지)

## 7. 주의사항

1. **인증 정보 보안**: 서비스 계정 키는 절대 Git에 커밋하지 말 것
2. **에러 처리**: 네트워크 오류, API 할당량 초과 등에 대한 예외 처리 필요
3. **비동기 처리**: Google Vision API 호출은 네트워크 I/O이므로 비동기로 처리하는 것을 고려
4. **결과 형식**: Google Vision과 PaddleOCR의 결과 형식이 다를 수 있으므로 정규화 단계에서 통일 필요

## 8. 추가 개선 사항

- [ ] 비동기 처리 (asyncio)
- [ ] 배치 처리 지원
- [ ] 에러 재시도 로직
- [ ] 비용 모니터링
- [ ] 결과 캐싱 최적화

