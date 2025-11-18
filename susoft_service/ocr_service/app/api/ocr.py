"""OCR API Endpoints"""
import os
import tempfile
import time
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, status
import httpx
from app.models import OCRResponse, OCRRequest, ErrorResponse
from app.auth import verify_token
from app.config import settings
from app.cache.idempotency import idempotency_cache
from app.ocr.paddle_engine import (
    PaddleOCREngine, 
    sort_blocks_by_reading_order,
    filter_small_boxes
)
from app.ocr.google_vision_engine import GoogleVisionEngine
from app.ocr.normalizer import normalize_blocks, generate_full_text


router = APIRouter(prefix="/ocr", tags=["OCR"])

# PaddleOCR 엔진 초기화 (싱글톤)
_paddle_engine: Optional[PaddleOCREngine] = None
_google_vision_engine: Optional[GoogleVisionEngine] = None


def get_paddle_engine() -> PaddleOCREngine:
    """PaddleOCR 엔진 싱글톤"""
    global _paddle_engine
    if _paddle_engine is None:
        _paddle_engine = PaddleOCREngine(
            lang="korean",
            use_angle_cls=True
        )
    return _paddle_engine


def get_google_vision_engine() -> GoogleVisionEngine:
    """Google Vision 엔진 싱글톤"""
    global _google_vision_engine
    if _google_vision_engine is None:
        _google_vision_engine = GoogleVisionEngine()
    return _google_vision_engine


async def download_file(url: str, max_size_mb: int = 20) -> str:
    """
    URL에서 파일 다운로드
    
    Args:
        url: 파일 URL
        max_size_mb: 최대 파일 크기 (MB)
        
    Returns:
        임시 파일 경로
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # 파일 크기 확인
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {max_size_mb}MB"
            )
        
        # 임시 파일에 저장
        suffix = os.path.splitext(url)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name


@router.post(
    "/extract",
    response_model=OCRResponse,
    responses={
        401: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="OCR 텍스트 추출",
    description="이미지에서 텍스트를 추출합니다. 파일 업로드 또는 URL 중 하나를 제공해야 합니다."
)
async def extract_ocr(
    idempotency_key: str = Form(..., description="중복 방지 키 (필수)"),
    engine: str = Form(default="paddle", description="OCR 엔진 (paddle|gcv)"),
    use_layout: bool = Form(default=False, description="LayoutParser 사용 여부 (MVP: false)"),
    file: Optional[UploadFile] = File(default=None, description="이미지 파일"),
    file_url: Optional[str] = Form(default=None, description="이미지 URL"),
    _token: Optional[str] = Depends(verify_token)
):
    """OCR 텍스트 추출 엔드포인트"""
    
    # 1. 입력 검증
    if not file and not file_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either 'file' or 'file_url' must be provided"
        )
    
    if file and file_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide only one of 'file' or 'file_url', not both"
        )
    
    if engine not in ["paddle", "gcv"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid engine. Must be 'paddle' or 'gcv'"
        )
    
    if engine == "gcv":
        if not settings.gcp_project or not settings.gcp_credentials_json:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Cloud Vision not configured. Set GCP_PROJECT and GCP_CREDENTIALS_JSON"
            )
    
    if use_layout:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="LayoutParser not implemented yet (MVP: use_layout=false)"
        )
    
    # 2. Idempotency 캐시 확인
    cached_result = await idempotency_cache.get(idempotency_key)
    if cached_result:
        return OCRResponse(**cached_result)
    
    tmp_file_path = None
    
    try:
        # 3. 파일 준비
        if file:
            # 파일 크기 확인
            content = await file.read()
            if len(content) > settings.max_file_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds {settings.max_file_mb}MB"
                )
            
            # 임시 파일 저장
            suffix = os.path.splitext(file.filename or "")[1] or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
        
        else:  # file_url
            tmp_file_path = await download_file(file_url, settings.max_file_mb)
        
        # 4. OCR 실행
        start_time = time.time()
        
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
        
        else:
            raise NotImplementedError(f"Unsupported engine: {engine}")
        
        total_duration_ms = int((time.time() - start_time) * 1000)
        
        # 5. 응답 생성
        response_data = {
            "engine": engine,
            "full_text": full_text,
            "blocks": [block.dict() for block in normalized_blocks],
            "meta": {
                "duration_ms": total_duration_ms,
                "ocr_duration_ms": ocr_duration_ms,
                "pages": 1
            },
            "idempotency_key": idempotency_key
        }
        
        # 6. 캐시 저장
        await idempotency_cache.set(idempotency_key, response_data)
        
        return OCRResponse(**response_data)
    
    except HTTPException:
        raise
    
    except Exception as e:
        import traceback
        error_detail = f"OCR processing failed: {str(e)}"
        print(f"ERROR: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
    
    finally:
        # 임시 파일 정리
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except:
                pass

