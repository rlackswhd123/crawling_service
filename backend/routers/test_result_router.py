"""
Test Result API Router
테스트 결과 조회 및 분석 API
"""
from typing import List
from fastapi import APIRouter, HTTPException, Query
from database.models import PromptTestResult
from services.test_result_service import TestResultService

router = APIRouter(prefix="/api/test-results", tags=["test-results"])
test_result_service = TestResultService()


@router.get("/recent", response_model=List[PromptTestResult])
async def get_recent_results(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    최근 테스트 결과 조회 (전체 프롬프트)

    Query Parameters:
    - limit: Maximum number of results (1-100, default: 20)

    Response (camelCase):
    ```json
    [
      {
        "testResultKey": 1,
        "promptKey": 5,
        "inputParams": {"feature": "furniture_removal"},
        "outputUrl": "data:image/png;base64,...",
        "executionTimeMs": 3250,
        "tokenCnt": 1024,
        "costAmount": 0.003,
        "successYn": 1,
        "errorMsg": null,
        "creDate": "2025-01-28T10:30:00",
        "creUserKey": 1,
        "deleteYn": 0,
        "promptKind": "bangkku/furniture_removal",
        "modelKind": "gemini",
        "promptText": "Remove all furniture..."
      }
    ]
    ```
    """
    try:
        results = await test_result_service.get_recent_results(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/failures", response_model=List[PromptTestResult])
async def get_failure_results(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    실패한 테스트 결과 조회 (디버깅용)

    Query Parameters:
    - limit: Maximum number of results (1-100, default: 20)

    Response: Array of failed test results (camelCase)
    Only returns results where successYn = 0 and errorMsg is not null
    """
    try:
        results = await test_result_service.get_failure_results(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt/{prompt_key}", response_model=List[PromptTestResult])
async def get_results_by_prompt(
    prompt_key: int,
    success_only: bool = Query(False, description="Only return successful results"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """
    특정 프롬프트의 테스트 결과 조회

    Path Parameter:
    - prompt_key: Prompt primary key

    Query Parameters (camelCase → snake_case 자동 변환):
    - successOnly: Only return successful results (default: false)
    - limit: Maximum number of results (1-100, default: 50)

    Response: Array of test results (camelCase, ordered by creDate desc)
    """
    try:
        results = await test_result_service.get_results_by_prompt(
            prompt_key=prompt_key,
            success_only=success_only,
            limit=limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{test_result_key}", response_model=PromptTestResult)
async def get_test_result(test_result_key: int):
    """
    특정 테스트 결과 조회

    Path Parameter:
    - test_result_key: Test result primary key

    Response: Test result object (camelCase)
    """
    result = await test_result_service.get_test_result(test_result_key)

    if not result:
        raise HTTPException(status_code=404, detail="Test result not found")

    return result


@router.get("/prompt/{prompt_key}/performance")
async def get_performance_stats(prompt_key: int):
    """
    프롬프트 성능 통계 조회

    Path Parameter:
    - prompt_key: Prompt primary key

    Response (camelCase):
    ```json
    {
      "totalTests": 150,
      "successCount": 142,
      "avgExecutionTime": 3250.5,
      "minExecutionTime": 2100,
      "maxExecutionTime": 5800,
      "avgTokenCnt": 1024,
      "totalCost": 0.45,
      "avgCost": 0.003
    }
    ```
    """
    result = await test_result_service.get_performance_stats(prompt_key)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No performance statistics found for this prompt"
        )

    return result
