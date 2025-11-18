"""
Prompt Repository
Business logic for prompts table
"""
from typing import Optional, Dict, Any, List
from repos.base import BaseRepository
from database.connection import get_db_cursor


class PromptRepository(BaseRepository):
    """Repository for prompts table"""

    def __init__(self):
        super().__init__(
            table_name='prompts',
            pk_column='prompt_key'
        )

    def get_default(self, prompt_kind: str) -> Optional[Dict[str, Any]]:
        """
        Get default prompt for a specific prompt_kind

        Args:
            prompt_kind: Service/feature path (e.g., 'bangkku/furniture_removal')

        Returns:
            Optional[Dict]: Default prompt or None
        """
        query = """
            SELECT * FROM prompts
            WHERE prompt_kind = %s AND is_default_yn = 1 AND delete_yn = 0
            LIMIT 1
        """
        return self.execute_one(query, (prompt_kind,))

    def get_by_kind(self, prompt_kind: str, include_non_default: bool = True) -> List[Dict[str, Any]]:
        """
        Get all prompts for a specific prompt_kind

        Args:
            prompt_kind: Service/feature path
            include_non_default: Include non-default prompts

        Returns:
            List[Dict]: List of prompts ordered by creation date desc
        """
        if include_non_default:
            where = "prompt_kind = %s"
        else:
            where = "prompt_kind = %s AND is_default_yn = 1"

        return self.list(
            where=where,
            params=(prompt_kind,),
            order_by="cre_date DESC"
        )

    def increment_use_cnt(self, prompt_key: int) -> bool:
        """
        Increment use count by 1

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if updated
        """
        query = """
            UPDATE prompts
            SET use_cnt = use_cnt + 1
            WHERE prompt_key = %s AND delete_yn = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (prompt_key,))
            return cursor.rowcount > 0

    def increment_success_cnt(self, prompt_key: int) -> bool:
        """
        Increment success count by 1

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if updated
        """
        query = """
            UPDATE prompts
            SET success_cnt = success_cnt + 1
            WHERE prompt_key = %s AND delete_yn = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (prompt_key,))
            return cursor.rowcount > 0

    def update_avg_rating(self, prompt_key: int) -> bool:
        """
        Recalculate and update average rating from prompt_ratings table

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if updated
        """
        query = """
            UPDATE prompts
            SET avg_rating = (
                SELECT AVG(rating_score)
                FROM prompt_ratings
                WHERE prompt_key = %s AND delete_yn = 0
            )
            WHERE prompt_key = %s AND delete_yn = 0
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (prompt_key, prompt_key))
            return cursor.rowcount > 0

    def set_as_default(self, prompt_key: int) -> bool:
        """
        Set a prompt as default (and unset others of same prompt_kind)

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if successful
        """
        # Get prompt_kind first
        prompt = self.get_by_id(prompt_key)
        if not prompt:
            return False

        prompt_kind = prompt['prompt_kind']

        # Transaction: Unset all defaults for this kind, then set new default
        query_unset = """
            UPDATE prompts
            SET is_default_yn = 0
            WHERE prompt_kind = %s AND delete_yn = 0
        """
        query_set = """
            UPDATE prompts
            SET is_default_yn = 1
            WHERE prompt_key = %s AND delete_yn = 0
        """

        with get_db_cursor() as cursor:
            cursor.execute(query_unset, (prompt_kind,))
            cursor.execute(query_set, (prompt_key,))
            return cursor.rowcount > 0

    def get_statistics(self, prompt_key: int) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a prompt

        Args:
            prompt_key: Prompt primary key

        Returns:
            Optional[Dict]: Statistics including test results count, avg execution time, etc.
        """
        query = """
            SELECT
                p.prompt_key,
                p.prompt_kind,
                p.use_cnt,
                p.success_cnt,
                p.avg_rating,
                COUNT(tr.test_result_key) as total_tests,
                AVG(tr.execution_time_ms) as avg_execution_time,
                AVG(tr.token_cnt) as avg_token_cnt,
                SUM(tr.cost_amount) as total_cost
            FROM prompts p
            LEFT JOIN prompt_test_results tr ON p.prompt_key = tr.prompt_key AND tr.delete_yn = 0
            WHERE p.prompt_key = %s AND p.delete_yn = 0
            GROUP BY p.prompt_key
        """
        return self.execute_one(query, (prompt_key,))
