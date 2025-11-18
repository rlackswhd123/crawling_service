"""
Rating Service
프롬프트 평가 비즈니스 로직
"""
from typing import Optional, List, Dict, Any
from database.models import PromptRating, RatingCreate
from repos.rating_repo import RatingRepository
from repos.prompt_repo import PromptRepository


class RatingService:
    """프롬프트 평가 Service"""

    def __init__(self):
        self.repo = RatingRepository()
        self.prompt_repo = PromptRepository()

    async def create_rating(self, request: RatingCreate) -> int:
        """
        프롬프트 평가 생성

        Args:
            request: RatingCreate 요청 모델

        Returns:
            int: 생성된 rating_key
        """
        data = {
            'prompt_key': request.prompt_key,
            'test_result_key': request.test_result_key,
            'rater_user_key': request.rater_user_key,
            'rating_score': request.rating_score,
            'rating_cmt': request.rating_cmt,
            'delete_yn': 0
        }

        # None 값 제거
        data = {k: v for k, v in data.items() if v is not None}

        rating_key = self.repo.create(data)

        # Update prompt's average rating
        self.prompt_repo.update_avg_rating(request.prompt_key)

        return rating_key

    async def get_rating_by_id(self, rating_key: int) -> Optional[PromptRating]:
        """
        평가 조회 (단일)

        Args:
            rating_key: 평가 primary key

        Returns:
            Optional[PromptRating]: 평가 객체 또는 None
        """
        result = self.repo.get_by_id(rating_key)
        if not result:
            return None

        return PromptRating(**result)

    async def get_ratings_by_prompt(
        self,
        prompt_key: int,
        limit: int = 50
    ) -> List[PromptRating]:
        """
        특정 프롬프트의 평가 목록 조회

        Args:
            prompt_key: 프롬프트 primary key
            limit: 최대 조회 개수

        Returns:
            List[PromptRating]: 평가 목록
        """
        results = self.repo.get_by_prompt_key(prompt_key, limit)
        return [PromptRating(**row) for row in results]

    async def get_average_rating(self, prompt_key: int) -> Optional[Dict[str, Any]]:
        """
        특정 프롬프트의 평균 평점 및 통계 조회

        Args:
            prompt_key: 프롬프트 primary key

        Returns:
            Optional[Dict]: 평균 평점 통계
        """
        return self.repo.get_average_rating(prompt_key)

    async def get_recent_ratings(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        최근 평가 목록 조회 (전체 프롬프트)

        Args:
            limit: 최대 조회 개수

        Returns:
            List[Dict]: 평가 목록 (프롬프트 정보 포함)
        """
        return self.repo.get_recent_ratings(limit)

    async def delete_rating(self, rating_key: int) -> bool:
        """
        평가 삭제 (Soft delete)

        Args:
            rating_key: 평가 primary key

        Returns:
            bool: 성공 여부
        """
        # Get rating to get prompt_key before deletion
        rating = self.repo.get_by_id(rating_key)
        if not rating:
            return False

        prompt_key = rating['prompt_key']

        # Delete rating
        success = self.repo.delete(rating_key)

        if success:
            # Update prompt's average rating
            self.prompt_repo.update_avg_rating(prompt_key)

        return success

    async def update_rating(
        self,
        rating_key: int,
        rating_score: Optional[int] = None,
        rating_cmt: Optional[str] = None
    ) -> bool:
        """
        평가 수정

        Args:
            rating_key: 평가 primary key
            rating_score: 별점 (1-5)
            rating_cmt: 코멘트

        Returns:
            bool: 성공 여부
        """
        data = {}
        if rating_score is not None:
            data['rating_score'] = rating_score
        if rating_cmt is not None:
            data['rating_cmt'] = rating_cmt

        if not data:
            return False

        return self.repo.update(rating_key, data)
