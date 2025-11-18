"""
Prompt Service
Business logic for prompt management
Each function has a single responsibility
"""
from typing import Optional, Dict, Any, List
from repos.prompt_repo import PromptRepository
from database.models import PromptCreate, PromptUpdate


class PromptService:
    """Service layer for prompt operations"""

    def __init__(self):
        self.repo = PromptRepository()

    async def get_default_prompt(self, prompt_kind: str) -> Optional[Dict[str, Any]]:
        """
        Get default prompt for a service/feature

        Args:
            prompt_kind: Service/feature path (e.g., 'bangkku/furniture_removal')

        Returns:
            Optional[Dict]: Default prompt or None if not found
        """
        return self.repo.get_default(prompt_kind)

    async def get_prompt_by_id(self, prompt_key: int) -> Optional[Dict[str, Any]]:
        """
        Get prompt by primary key

        Args:
            prompt_key: Prompt primary key

        Returns:
            Optional[Dict]: Prompt data or None
        """
        return self.repo.get_by_id(prompt_key)

    async def get_prompts_by_kind(
        self,
        prompt_kind: str,
        include_non_default: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all prompts for a service/feature

        Args:
            prompt_kind: Service/feature path
            include_non_default: Include non-default prompts

        Returns:
            List[Dict]: List of prompts
        """
        return self.repo.get_by_kind(prompt_kind, include_non_default)

    async def create_prompt(self, prompt_data: PromptCreate) -> int:
        """
        Create a new prompt

        Args:
            prompt_data: Prompt creation data

        Returns:
            int: Created prompt key
        """
        data = prompt_data.model_dump()
        return self.repo.create(data)

    async def update_prompt(self, prompt_key: int, prompt_data: PromptUpdate) -> bool:
        """
        Update prompt text or default status

        Args:
            prompt_key: Prompt primary key
            prompt_data: Update data

        Returns:
            bool: True if updated
        """
        data = prompt_data.model_dump(exclude_none=True)
        if not data:
            return False
        return self.repo.update(prompt_key, data)

    async def increment_usage(self, prompt_key: int) -> bool:
        """
        Increment prompt use count by 1
        Single responsibility: usage tracking only

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if incremented
        """
        return self.repo.increment_use_cnt(prompt_key)

    async def increment_success(self, prompt_key: int) -> bool:
        """
        Increment prompt success count by 1
        Single responsibility: success tracking only

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if incremented
        """
        return self.repo.increment_success_cnt(prompt_key)

    async def set_as_default(self, prompt_key: int) -> bool:
        """
        Set a prompt as default for its prompt_kind
        Unsets other defaults automatically

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if set as default
        """
        return self.repo.set_as_default(prompt_key)

    async def update_avg_rating(self, prompt_key: int) -> bool:
        """
        Recalculate average rating from ratings table
        Called after rating changes

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if updated
        """
        return self.repo.update_avg_rating(prompt_key)

    async def get_statistics(self, prompt_key: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive statistics for a prompt
        Includes test results, execution times, costs

        Args:
            prompt_key: Prompt primary key

        Returns:
            Optional[Dict]: Statistics or None
        """
        return self.repo.get_statistics(prompt_key)

    async def delete_prompt(self, prompt_key: int) -> bool:
        """
        Soft delete a prompt

        Args:
            prompt_key: Prompt primary key

        Returns:
            bool: True if deleted
        """
        return self.repo.delete(prompt_key)
