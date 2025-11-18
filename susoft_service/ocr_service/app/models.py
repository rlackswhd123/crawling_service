"""Pydantic Models for API"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class OCRBlock(BaseModel):
    """OCR 블록 정보"""
    type: str = Field(default="paragraph", description="블록 타입")
    text: str = Field(description="추출된 텍스트")
    bbox: List[float] = Field(description="[x1, y1, x2, y2] 좌표")
    page: int = Field(default=1, description="페이지 번호")
    confidence: Optional[float] = Field(default=None, description="신뢰도 (0-1)")


class OCRRequest(BaseModel):
    """OCR 요청"""
    engine: Literal["paddle", "gcv"] = Field(default="paddle", description="OCR 엔진")
    use_layout: bool = Field(default=False, description="LayoutParser 사용 여부")
    idempotency_key: str = Field(description="중복 방지 키 (필수)")
    file_url: Optional[str] = Field(default=None, description="이미지 URL (file과 택1)")


class OCRResponse(BaseModel):
    """OCR 응답"""
    engine: str = Field(description="사용된 OCR 엔진")
    full_text: str = Field(description="병합된 전체 텍스트")
    blocks: List[OCRBlock] = Field(description="정규화된 블록 리스트")
    meta: dict = Field(description="메타 정보 (duration_ms, pages 등)")
    idempotency_key: str = Field(description="요청에 사용된 idempotency_key")


class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str = Field(description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="상세 정보")

