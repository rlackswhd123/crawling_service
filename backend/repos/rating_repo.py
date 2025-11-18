"""
Rating Repository
프롬프트 평가 데이터 접근 레이어
"""
from typing import Optional, List, Dict, Any
from repos.base import BaseRepository


class RatingRepository(BaseRepository):
    """프롬프트 평가 Repository"""

    def __init__(self):
        super().__init__(
            table_name='saeum_ai_api.prompt_ratings',
            pk_column='rating_key'
        )

    def get_by_prompt_key(self, prompt_key: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        특정 프롬프트의 평가 목록 조회

        Args:
            prompt_key: 프롬프트 primary key
            limit: 최대 조회 개수

        Returns:
            List[Dict]: 평가 목록
        """
        return self.list(
            where="prompt_key = %s",
            params=(prompt_key,),
            order_by="cre_date DESC",
            limit=limit
        )

    def get_by_test_result_key(self, test_result_key: int) -> List[Dict[str, Any]]:
        """
        특정 테스트 결과의 평가 목록 조회

        Args:
            test_result_key: 테스트 결과 primary key

        Returns:
            List[Dict]: 평가 목록
        """
        return self.list(
            where="test_result_key = %s",
            params=(test_result_key,),
            order_by="cre_date DESC"
        )

    def get_average_rating(self, prompt_key: int) -> Optional[Dict[str, Any]]:
        """
        특정 프롬프트의 평균 평점 및 통계 조회

        Args:
            prompt_key: 프롬프트 primary key

        Returns:
            Optional[Dict]: 평균 평점 통계
            {
                'avg_rating': 4.5,
                'total_ratings': 10,
                'rating_distribution': {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4}
            }
        """
        query = """
            SELECT
                ROUND(AVG(rating_score), 2) as avg_rating,
                COUNT(*) as total_ratings,
                COUNT(CASE WHEN rating_score = 1 THEN 1 END) as rating_1_count,
                COUNT(CASE WHEN rating_score = 2 THEN 1 END) as rating_2_count,
                COUNT(CASE WHEN rating_score = 3 THEN 1 END) as rating_3_count,
                COUNT(CASE WHEN rating_score = 4 THEN 1 END) as rating_4_count,
                COUNT(CASE WHEN rating_score = 5 THEN 1 END) as rating_5_count
            FROM saeum_ai_api.prompt_ratings
            WHERE prompt_key = %s AND delete_yn = 0
        """
        result = self.execute_one(query, (prompt_key,))

        if not result or result['total_ratings'] == 0:
            return None

        return {
            'avg_rating': float(result['avg_rating']) if result['avg_rating'] else 0,
            'total_ratings': result['total_ratings'],
            'rating_distribution': {
                '1': result['rating_1_count'],
                '2': result['rating_2_count'],
                '3': result['rating_3_count'],
                '4': result['rating_4_count'],
                '5': result['rating_5_count']
            }
        }

    def get_recent_ratings(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        최근 평가 목록 조회 (전체 프롬프트)

        Args:
            limit: 최대 조회 개수

        Returns:
            List[Dict]: 평가 목록
        """
        query = """
            SELECT
                r.*,
                p.prompt_kind,
                p.prompt_text
            FROM saeum_ai_api.prompt_ratings r
            LEFT JOIN saeum_ai_api.prompts p ON r.prompt_key = p.prompt_key
            WHERE r.delete_yn = 0
            ORDER BY r.cre_date DESC
            LIMIT %s
        """
        return self.execute(query, (limit,))
