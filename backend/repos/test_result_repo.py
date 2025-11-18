"""
Test Result Repository
Business logic for prompt_test_results table
"""
from typing import List, Dict, Any
from repos.base import BaseRepository


class TestResultRepository(BaseRepository):
    """Repository for prompt_test_results table"""

    def __init__(self):
        super().__init__(
            table_name='prompt_test_results',
            pk_column='test_result_key'
        )

    def get_by_prompt(
        self,
        prompt_key: int,
        success_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get test results for a specific prompt

        Args:
            prompt_key: Prompt primary key
            success_only: If True, only return successful results
            limit: Maximum number of results

        Returns:
            List[Dict]: Test results ordered by creation date desc
        """
        where = "prompt_key = %s"
        params = [prompt_key]

        if success_only:
            where += " AND success_yn = 1"

        return self.list(
            where=where,
            params=tuple(params),
            order_by="cre_date DESC",
            limit=limit
        )

    def get_recent_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent test results across all prompts

        Args:
            limit: Maximum number of results

        Returns:
            List[Dict]: Recent test results with prompt info
        """
        query = """
            SELECT
                tr.*,
                p.prompt_kind,
                p.model_kind,
                p.prompt_text
            FROM prompt_test_results tr
            JOIN prompts p ON tr.prompt_key = p.prompt_key AND p.delete_yn = 0
            WHERE tr.delete_yn = 0
            ORDER BY tr.cre_date DESC
            LIMIT %s
        """
        return self.execute(query, (limit,))

    def get_failure_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent failure results for debugging

        Args:
            limit: Maximum number of results

        Returns:
            List[Dict]: Failed test results with error messages
        """
        return self.list(
            where="success_yn = 0 AND error_msg IS NOT NULL",
            order_by="cre_date DESC",
            limit=limit
        )

    def get_performance_stats(self, prompt_key: int) -> Dict[str, Any]:
        """
        Get performance statistics for a prompt

        Args:
            prompt_key: Prompt primary key

        Returns:
            Dict: Performance stats (avg/min/max execution time, tokens, cost)
        """
        query = """
            SELECT
                COUNT(*) as total_tests,
                SUM(CASE WHEN success_yn = 1 THEN 1 ELSE 0 END) as success_count,
                AVG(execution_time_ms) as avg_execution_time,
                MIN(execution_time_ms) as min_execution_time,
                MAX(execution_time_ms) as max_execution_time,
                AVG(token_cnt) as avg_token_cnt,
                SUM(cost_amount) as total_cost,
                AVG(cost_amount) as avg_cost
            FROM prompt_test_results
            WHERE prompt_key = %s AND delete_yn = 0
        """
        result = self.execute_one(query, (prompt_key,))
        return result if result else {}
