"""Google Cloud Vision Engine Wrapper"""
import time
from typing import List, Tuple
from google.cloud import vision
from google.oauth2 import service_account
from google.api_core import exceptions as gcp_exceptions
import json
from app.config import settings


class GoogleVisionEngine:
    """Google Cloud Vision OCR 엔진 래퍼"""
    
    def __init__(self):
        """Google Vision 클라이언트 초기화"""
        credentials = None
        
        try:
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
        except Exception as e:
            raise ValueError(f"Failed to initialize Google Vision client: {str(e)}")
    
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
        
        # OCR 실행 (document_text_detection 사용)
        try:
            response = self.client.document_text_detection(image=image)
            
            # 에러 체크
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            document = response.full_text_annotation
            
        except gcp_exceptions.PermissionDenied as e:
            error_msg = str(e)
            if "BILLING_DISABLED" in error_msg or "billing" in error_msg.lower():
                raise Exception(
                    "Google Cloud Vision API requires billing to be enabled. "
                    "Please enable billing in your GCP project. "
                    "Note: First 1,000 requests/month are free. "
                    f"Error details: {error_msg[:200]}"
                )
            raise Exception(f"Permission denied. Check GCP credentials and API permissions: {error_msg[:200]}")
        except gcp_exceptions.InvalidArgument as e:
            raise Exception(f"Invalid argument: {str(e)[:200]}")
        except Exception as e:
            raise Exception(f"Google Vision API call failed: {str(e)[:200]}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 결과 정규화 - document_text_detection의 계층 구조 처리
        blocks = []
        if document and hasattr(document, 'pages'):
            # pages → blocks → paragraphs → words 계층 구조 순회
            for page in document.pages:
                if not hasattr(page, 'blocks'):
                    continue
                    
                for block in page.blocks:
                    if not hasattr(block, 'paragraphs'):
                        continue
                    
                    for paragraph in block.paragraphs:
                        if not hasattr(paragraph, 'words'):
                            continue
                        
                        for word in paragraph.words:
                            # word의 bounding_box 추출
                            if not hasattr(word, 'bounding_box') or not word.bounding_box:
                                continue
                            
                            vertices = word.bounding_box.vertices
                            if not vertices or len(vertices) < 4:
                                continue
                            
                            # bbox를 [x1, y1, x2, y2] 형식으로 변환
                            x_coords = [v.x for v in vertices if hasattr(v, 'x')]
                            y_coords = [v.y for v in vertices if hasattr(v, 'y')]
                            
                            if not x_coords or not y_coords:
                                continue
                            
                            # word의 symbols를 합쳐서 텍스트 생성
                            text = ""
                            confidence_sum = 0.0
                            confidence_count = 0
                            
                            if hasattr(word, 'symbols'):
                                for symbol in word.symbols:
                                    if hasattr(symbol, 'text'):
                                        text += symbol.text
                                    # confidence 정보 수집
                                    if hasattr(symbol, 'confidence'):
                                        confidence_sum += symbol.confidence
                                        confidence_count += 1
                            
                            # 평균 confidence 계산
                            avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 1.0
                            
                            blocks.append({
                                "bbox": [
                                    min(x_coords),
                                    min(y_coords),
                                    max(x_coords),
                                    max(y_coords)
                                ],
                                "text": text,
                                "confidence": avg_confidence
                            })
        
        return blocks, duration_ms

