"""
Test Result Service
Business logic for test result management
Each function has a single responsibility
"""
from typing import Dict, Any, List, Optional
from repos.test_result_repo import TestResultRepository
from database.models import TestResultCreate


class TestResultService:
    """Service layer for test result operations"""

    def __init__(self):
        self.repo = TestResultRepository()

    async def create_test_result(self, result_data: TestResultCreate) -> int:
        """
        Create a new test result record

        Args:
            result_data: Test result data

        Returns:
            int: Created test_result_key
        """
        data = result_data.model_dump()
        return self.repo.create(data)

    async def get_test_result(self, test_result_key: int) -> Optional[Dict[str, Any]]:
        """
        Get test result by primary key

        Args:
            test_result_key: Test result primary key

        Returns:
            Optional[Dict]: Test result data or None
        """
        return self.repo.get_by_id(test_result_key)

    async def get_results_by_prompt(
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
        return self.repo.get_by_prompt(prompt_key, success_only, limit)

    async def get_recent_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent test results across all prompts
        Includes prompt information via JOIN

        Args:
            limit: Maximum number of results

        Returns:
            List[Dict]: Recent test results with prompt info
        """
        return self.repo.get_recent_results(limit)

    async def get_failure_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent failure results for debugging
        Only returns results with error messages

        Args:
            limit: Maximum number of results

        Returns:
            List[Dict]: Failed test results
        """
        return self.repo.get_failure_results(limit)

    async def get_performance_stats(self, prompt_key: int) -> Dict[str, Any]:
        """
        Get performance statistics for a prompt
        Single responsibility: performance metrics only

        Args:
            prompt_key: Prompt primary key

        Returns:
            Dict: Performance stats (avg/min/max execution time, tokens, cost)
        """
        return self.repo.get_performance_stats(prompt_key)

    async def delete_test_result(self, test_result_key: int) -> bool:
        """
        Soft delete a test result

        Args:
            test_result_key: Test result primary key

        Returns:
            bool: True if deleted
        """
        return self.repo.delete(test_result_key)
