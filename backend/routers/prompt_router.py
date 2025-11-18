"""
Prompt Management API Router
프롬프트 CRUD 및 관리 API
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from database.models import Prompt, PromptCreate, PromptUpdate, PromptRating, RatingCreate
from services.prompt_service import PromptService
from services.rating_service import RatingService
from utils.file_storage import save_multiple_prompt_images

router = APIRouter(prefix="/api/prompts", tags=["prompts"])
prompt_service = PromptService()
rating_service = RatingService()


@router.post("/", response_model=Prompt, status_code=201)
async def create_prompt(request: PromptCreate):
    """
    프롬프트 생성

    Request (JSON - camelCase):
    ```json
    {
      "promptKind": "bangkku/furniture_removal",
      "modelKind": "gemini",
      "promptText": "Remove all furniture...",
      "isDefaultYn": 1
    }
    ```

    Response (JSON - camelCase):
    ```json
    {
      "promptKey": 1,
      "promptKind": "bangkku/furniture_removal",
      "modelKind": "gemini",
      "promptText": "Remove all furniture...",
      "isDefaultYn": 1,
      "useCnt": 0,
      "successCnt": 0,
      "avgRating": null,
      "creDate": "2025-01-28T10:30:00",
      "creUserKey": null,
      "updDate": null,
      "updUserKey": null,
      "deleteYn": 0
    }
    ```
    """
    try:
        prompt_key = await prompt_service.create_prompt(request)
        result = await prompt_service.get_prompt_by_id(prompt_key)

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create prompt")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/with-images", response_model=Prompt, status_code=201)
async def create_prompt_with_images(
    prompt_kind: str = Form(...),
    model_kind: Optional[str] = Form(None),
    prompt_text: str = Form(...),
    is_default_yn: int = Form(0),
    images: List[UploadFile] = File(default=[])
):
    """
    프롬프트 생성 (이미지 포함)

    Request (multipart/form-data):
    - promptKind: Service/feature path (required)
    - modelKind: AI model identifier (optional)
    - promptText: Prompt content (required)
    - isDefaultYn: Default flag (0 or 1, default: 0)
    - images: Image files (optional, multiple files supported)

    Response: Prompt object (camelCase)
    """
    try:
        # Save images to file system and get URLs
        image_urls = []
        if images:
            image_urls = await save_multiple_prompt_images(images)

        # Create prompt with image URLs
        request = PromptCreate(
            prompt_kind=prompt_kind,
            model_kind=model_kind,
            prompt_text=prompt_text,
            is_default_yn=is_default_yn,
            input_images=image_urls
        )

        prompt_key = await prompt_service.create_prompt(request)
        result = await prompt_service.get_prompt_by_id(prompt_key)

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create prompt")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_key}", response_model=Prompt)
async def get_prompt(prompt_key: int):
    """
    프롬프트 조회

    Path Parameter:
    - prompt_key: Prompt primary key

    Response: Prompt object (camelCase)
    """
    result = await prompt_service.get_prompt_by_id(prompt_key)

    if not result:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return result


@router.get("/", response_model=List[Prompt])
async def list_prompts(
    prompt_kind: Optional[str] = Query(None, alias="promptKind", description="Filter by service/feature path"),
    include_non_default: bool = Query(True, alias="includeNonDefault", description="Include non-default prompts")
):
    """
    프롬프트 목록 조회

    Query Parameters (자동 camelCase → snake_case 변환):
    - promptKind: Service/feature path (e.g., "bangkku/furniture_removal")
    - includeNonDefault: Include non-default prompts (default: true)

    Examples:
    - GET /api/prompts?promptKind=bangkku/furniture_removal
    - GET /api/prompts?promptKind=bangkku/furniture_removal&includeNonDefault=false

    Response: Array of Prompt objects (camelCase)
    """
    try:
        if prompt_kind:
            results = await prompt_service.get_prompts_by_kind(
                prompt_kind=prompt_kind,
                include_non_default=include_non_default
            )
        else:
            # Get all prompts
            results = await prompt_service.get_prompts_by_kind(
                prompt_kind="",
                include_non_default=include_non_default
            )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{prompt_key}", response_model=Prompt)
async def update_prompt(prompt_key: int, request: PromptUpdate):
    """
    프롬프트 수정

    Request (JSON - camelCase, partial update):
    ```json
    {
      "promptText": "Updated prompt text...",
      "isDefaultYn": 0
    }
    ```

    Response: Updated Prompt object (camelCase)
    """
    # Check if prompt exists
    existing = await prompt_service.get_prompt_by_id(prompt_key)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Update
    success = await prompt_service.update_prompt(prompt_key, request)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update prompt")

    # Return updated prompt
    result = await prompt_service.get_prompt_by_id(prompt_key)
    return result


@router.delete("/{prompt_key}", status_code=204)
async def delete_prompt(prompt_key: int):
    """
    프롬프트 삭제 (Soft delete)

    Path Parameter:
    - prompt_key: Prompt primary key

    Response: 204 No Content
    """
    success = await prompt_service.delete_prompt(prompt_key)

    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return None


@router.post("/{prompt_key}/set-default", response_model=Prompt)
async def set_as_default(prompt_key: int):
    """
    기본 프롬프트로 설정
    같은 prompt_kind의 다른 프롬프트들은 자동으로 is_default_yn = 0 설정됨

    Path Parameter:
    - prompt_key: Prompt primary key

    Response: Updated Prompt object (camelCase)
    """
    success = await prompt_service.set_as_default(prompt_key)

    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Return updated prompt
    result = await prompt_service.get_prompt_by_id(prompt_key)
    return result


@router.get("/{prompt_key}/statistics")
async def get_statistics(prompt_key: int):
    """
    프롬프트 통계 조회

    Path Parameter:
    - prompt_key: Prompt primary key

    Response (camelCase):
    ```json
    {
      "promptKey": 1,
      "promptKind": "bangkku/furniture_removal",
      "useCnt": 150,
      "successCnt": 142,
      "avgRating": 4.5,
      "totalTests": 150,
      "avgExecutionTime": 3250.5,
      "avgTokenCnt": 1024,
      "totalCost": 0.45
    }
    ```
    """
    result = await prompt_service.get_statistics(prompt_key)

    if not result:
        raise HTTPException(status_code=404, detail="Prompt not found or no statistics available")

    return result


# ==================== Rating Endpoints ====================

@router.post("/{prompt_key}/ratings", response_model=PromptRating, status_code=201)
async def create_rating(prompt_key: int, request: RatingCreate):
    """
    프롬프트 평가 생성

    Path Parameter:
    - prompt_key: Prompt primary key

    Request (JSON - camelCase):
    ```json
    {
      "raterUserKey": 1,
      "ratingScore": 5,
      "ratingCmt": "이 프롬프트 정말 좋네요! 결과가 훌륭합니다."
    }
    ```

    Response: PromptRating object (camelCase)
    """
    # Override prompt_key from path parameter
    request.prompt_key = prompt_key

    # Validate rating_score (1-5)
    if not 1 <= request.rating_score <= 5:
        raise HTTPException(status_code=400, detail="Rating score must be between 1 and 5")

    try:
        rating_key = await rating_service.create_rating(request)
        result = await rating_service.get_rating_by_id(rating_key)

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create rating")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_key}/ratings", response_model=List[PromptRating])
async def get_ratings(
    prompt_key: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of ratings")
):
    """
    특정 프롬프트의 평가 목록 조회

    Path Parameter:
    - prompt_key: Prompt primary key

    Query Parameter:
    - limit: 최대 조회 개수 (default: 50, max: 100)

    Response: Array of PromptRating objects (camelCase)
    """
    try:
        results = await rating_service.get_ratings_by_prompt(prompt_key, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_key}/ratings/average")
async def get_average_rating(prompt_key: int):
    """
    특정 프롬프트의 평균 평점 및 통계 조회

    Path Parameter:
    - prompt_key: Prompt primary key

    Response (camelCase):
    ```json
    {
      "avgRating": 4.5,
      "totalRatings": 10,
      "ratingDistribution": {
        "1": 0,
        "2": 1,
        "3": 2,
        "4": 3,
        "5": 4
      }
    }
    ```
    """
    result = await rating_service.get_average_rating(prompt_key)

    if not result:
        raise HTTPException(status_code=404, detail="No ratings found for this prompt")

    return result
