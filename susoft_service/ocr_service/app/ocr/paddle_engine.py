"""PaddleOCR Engine Wrapper"""
import time
from typing import List, Tuple, Optional
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image


class PaddleOCREngine:
    """PaddleOCR 엔진 래퍼"""
    
    def __init__(self, lang: str = "korean", use_angle_cls: bool = True):
        """
        PaddleOCR 초기화
        
        Args:
            lang: 언어 설정 ("korean", "korean_english")
            use_angle_cls: 텍스트 방향 분류 사용 여부
        """
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            use_gpu=False,  # CPU 사용 (GPU 환경이면 True로 변경)
            show_log=False
        )
        
    def extract(self, image_path: str) -> Tuple[List[dict], int]:
        """
        이미지에서 텍스트 추출
        
        Args:
            image_path: 이미지 파일 경로
            
        Returns:
            (결과 리스트, 소요 시간(ms))
        """
        start_time = time.time()
        
        # OCR 실행
        result = self.ocr.ocr(image_path, cls=True)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 결과 정규화
        blocks = []
        if result and result[0]:
            for line in result[0]:
                if not line:
                    continue
                    
                bbox = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = line[1]  # (text, confidence)
                
                # bbox를 [x1, y1, x2, y2] 형식으로 변환
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                normalized_bbox = [
                    min(x_coords),
                    min(y_coords),
                    max(x_coords),
                    max(y_coords)
                ]
                
                blocks.append({
                    "bbox": normalized_bbox,
                    "text": text_info[0],
                    "confidence": text_info[1]
                })
        
        return blocks, duration_ms


def sort_blocks_by_reading_order(blocks: List[dict]) -> List[dict]:
    """
    블록을 읽기 순서대로 정렬 (위→아래, 왼쪽→오른쪽)
    
    Args:
        blocks: OCR 블록 리스트
        
    Returns:
        정렬된 블록 리스트
    """
    if not blocks:
        return blocks
    
    # y 좌표로 먼저 정렬 (위에서 아래로)
    # 같은 줄로 간주되는 블록들은 x 좌표로 정렬 (왼쪽에서 오른쪽으로)
    
    # 평균 높이 계산
    avg_height = sum(block["bbox"][3] - block["bbox"][1] for block in blocks) / len(blocks)
    threshold = avg_height * 0.5  # 같은 줄로 간주할 y 좌표 차이 임계값
    
    # y 좌표 기준으로 먼저 정렬
    sorted_blocks = sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))
    
    # 같은 줄의 블록들을 그룹화하고 x 좌표로 재정렬
    lines = []
    current_line = []
    current_y = None
    
    for block in sorted_blocks:
        y = block["bbox"][1]
        
        if current_y is None:
            current_y = y
            current_line = [block]
        elif abs(y - current_y) <= threshold:
            current_line.append(block)
        else:
            # 현재 줄을 x 좌표로 정렬하여 저장
            current_line.sort(key=lambda b: b["bbox"][0])
            lines.extend(current_line)
            
            current_line = [block]
            current_y = y
    
    # 마지막 줄 처리
    if current_line:
        current_line.sort(key=lambda b: b["bbox"][0])
        lines.extend(current_line)
    
    return lines


def filter_small_boxes(blocks: List[dict], min_width: int = 10, min_height: int = 10) -> List[dict]:
    """
    너무 작은 박스 제거 (노이즈 필터링)
    
    Args:
        blocks: OCR 블록 리스트
        min_width: 최소 너비
        min_height: 최소 높이
        
    Returns:
        필터링된 블록 리스트
    """
    filtered = []
    for block in blocks:
        bbox = block["bbox"]
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        if width >= min_width and height >= min_height:
            filtered.append(block)
    
    return filtered

