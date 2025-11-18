"""OCR 결과 정규화"""
from typing import List
from app.models import OCRBlock


def normalize_blocks(raw_blocks: List[dict], page: int = 1) -> List[OCRBlock]:
    """
    원시 OCR 결과를 정규화된 블록으로 변환
    
    Args:
        raw_blocks: 원시 OCR 블록 리스트
        page: 페이지 번호
        
    Returns:
        정규화된 OCR 블록 리스트
    """
    normalized = []
    
    for block in raw_blocks:
        normalized.append(OCRBlock(
            type="paragraph",
            text=block["text"],
            bbox=block["bbox"],
            page=page,
            confidence=block.get("confidence")
        ))
    
    return normalized


def generate_full_text(blocks: List[OCRBlock]) -> str:
    """
    블록들을 병합하여 전체 텍스트 생성
    
    Args:
        blocks: 정규화된 OCR 블록 리스트
        
    Returns:
        병합된 전체 텍스트
    """
    if not blocks:
        return ""
    
    # 각 블록의 텍스트를 줄바꿈으로 연결
    texts = [block.text for block in blocks if block.text.strip()]
    return "\n".join(texts)

