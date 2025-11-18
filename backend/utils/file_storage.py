"""
파일 저장 유틸리티

프롬프트 관련 이미지 파일들을 파일 시스템에 저장하고 URL을 반환합니다.
"""
import os
import uuid
from pathlib import Path
from typing import List
from fastapi import UploadFile

# 프로젝트 루트 기준 static 디렉토리 경로
STATIC_DIR = Path(__file__).parent.parent / "static"
PROMPTS_IMAGE_DIR = STATIC_DIR / "prompts" / "images"

# 디렉토리가 없으면 생성
PROMPTS_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


async def save_prompt_image(file: UploadFile) -> str:
    """
    프롬프트 관련 이미지를 파일 시스템에 저장하고 URL 반환

    Args:
        file: FastAPI UploadFile 객체

    Returns:
        str: 저장된 이미지의 URL 경로 (예: /static/prompts/images/abc123.jpg)
    """
    # 파일 확장자 추출
    original_filename = file.filename or "image.jpg"
    file_ext = Path(original_filename).suffix

    # UUID로 고유한 파일명 생성
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = PROMPTS_IMAGE_DIR / unique_filename

    # 파일 저장
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # URL 반환 (static 기준 상대 경로)
    return f"/static/prompts/images/{unique_filename}"


async def save_multiple_prompt_images(files: List[UploadFile]) -> List[str]:
    """
    여러 프롬프트 이미지를 파일 시스템에 저장하고 URL 리스트 반환

    Args:
        files: FastAPI UploadFile 객체 리스트

    Returns:
        List[str]: 저장된 이미지들의 URL 경로 리스트
    """
    urls = []
    for file in files:
        url = await save_prompt_image(file)
        urls.append(url)
    return urls


def delete_prompt_image(image_url: str) -> bool:
    """
    프롬프트 이미지 파일 삭제

    Args:
        image_url: 삭제할 이미지의 URL (예: /static/prompts/images/abc123.jpg)

    Returns:
        bool: 삭제 성공 여부
    """
    try:
        # URL에서 파일명 추출
        filename = Path(image_url).name
        file_path = PROMPTS_IMAGE_DIR / filename

        if file_path.exists():
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting image {image_url}: {e}")
        return False
