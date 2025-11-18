"""
Database Models
Pydantic models mapped to PostgreSQL tables
"""
from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """
    camelCase 자동 변환 Base 모델
    - JSON: camelCase (Frontend 호환)
    - Python: snake_case (내부 사용)
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # snake_case도 허용 (Python 내부 사용)
        from_attributes=True    # ORM 지원 (asyncpg DictRow)
    )


class BaseDBModel(CamelCaseModel):
    """Base model with common audit fields"""
    cre_date: Optional[datetime] = None
    cre_user_key: Optional[int] = None
    upd_date: Optional[datetime] = None
    upd_user_key: Optional[int] = None
    delete_yn: int = 0


class Member(BaseDBModel):
    """Member table model"""
    user_key: Optional[int] = None
    user_name: str
    user_email: Optional[str] = None
    role_kind: Optional[str] = None  # 'developer', 'operator'


class Prompt(BaseDBModel):
    """Prompts table model"""
    prompt_key: Optional[int] = None
    prompt_kind: str  # 'bangkku/furniture_removal'
    model_kind: Optional[str] = None  # 'gemini', 'veo', 'gpt4'
    prompt_text: str
    is_default_yn: int = 0
    use_cnt: int = 0
    success_cnt: int = 0
    avg_rating: Optional[float] = None
    input_images: Optional[List[str]] = None  # URLs to input images

    @field_validator('input_images', mode='before')
    @classmethod
    def validate_input_images(cls, v):
        """Convert None, empty dict, or invalid values to empty list"""
        if v is None or v == {} or (isinstance(v, dict) and not v):
            return []
        if isinstance(v, list):
            return v
        return []


class PromptTestResult(BaseDBModel):
    """Prompt test results table model"""
    test_result_key: Optional[int] = None
    prompt_key: int
    input_params: Optional[dict[str, Any]] = None  # JSON field
    output_url: Optional[str] = None
    execution_time_ms: Optional[int] = None
    token_cnt: Optional[int] = None
    cost_amount: Optional[float] = None
    success_yn: int
    error_msg: Optional[str] = None


class PromptRating(BaseDBModel):
    """Prompt ratings table model"""
    rating_key: Optional[int] = None
    prompt_key: Optional[int] = None
    test_result_key: Optional[int] = None
    rater_user_key: int
    rating_score: int  # 1-5
    rating_cmt: Optional[str] = None


# Request/Response models for API

class PromptCreate(CamelCaseModel):
    """Request model for creating a prompt"""
    prompt_kind: str
    model_kind: Optional[str] = None
    prompt_text: str
    is_default_yn: int = 0
    input_images: Optional[List[str]] = None  # URLs to input images

    @field_validator('input_images', mode='before')
    @classmethod
    def validate_input_images(cls, v):
        """Convert None to empty list"""
        if v is None:
            return []
        return v


class PromptUpdate(CamelCaseModel):
    """Request model for updating a prompt"""
    prompt_text: Optional[str] = None
    is_default_yn: Optional[int] = None


class TestResultCreate(CamelCaseModel):
    """Request model for creating a test result"""
    prompt_key: int
    input_params: Optional[dict[str, Any]] = None
    output_url: Optional[str] = None
    execution_time_ms: Optional[int] = None
    token_cnt: Optional[int] = None
    cost_amount: Optional[float] = None
    success_yn: int
    error_msg: Optional[str] = None


class RatingCreate(CamelCaseModel):
    """Request model for creating a rating"""
    prompt_key: Optional[int] = None
    test_result_key: Optional[int] = None
    rater_user_key: int
    rating_score: int  # 1-5
    rating_cmt: Optional[str] = None
