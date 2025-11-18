"""
Base Repository
Common CRUD operations for all repositories
"""
import json
from datetime import datetime
from typing import Optional, TypeVar, Generic, List, Dict, Any
from database.connection import get_db_cursor

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository with common CRUD operations

    Usage:
        class PromptRepository(BaseRepository):
            def __init__(self):
                super().__init__(
                    table_name='prompts',
                    pk_column='prompt_key'
                )
    """

    def __init__(self, table_name: str, pk_column: str):
        self.table_name = table_name
        self.pk_column = pk_column

    def create(self, data: Dict[str, Any]) -> int:
        """
        Insert a new record

        Args:
            data: Dictionary of column:value pairs

        Returns:
            int: Primary key of inserted record
        """
        # Convert lists/dicts to JSON strings for JSONB columns
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                # Serialize Python list/dict to JSON string for JSONB columns
                processed_data[key] = json.dumps(value)
            else:
                processed_data[key] = value

        # Add creation timestamp
        processed_data['cre_date'] = datetime.now()

        columns = ', '.join(processed_data.keys())
        placeholders = ', '.join(['%s'] * len(processed_data))
        values = tuple(processed_data.values())

        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING {self.pk_column}
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            return result[self.pk_column]

    def get_by_id(self, pk_value: int) -> Optional[Dict[str, Any]]:
        """
        Get record by primary key

        Args:
            pk_value: Primary key value

        Returns:
            Optional[Dict]: Record as dictionary or None
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {self.pk_column} = %s AND delete_yn = 0
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (pk_value,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def update(self, pk_value: int, data: Dict[str, Any]) -> bool:
        """
        Update a record

        Args:
            pk_value: Primary key value
            data: Dictionary of column:value pairs to update

        Returns:
            bool: True if updated, False if not found
        """
        # Convert lists/dicts to JSON strings for JSONB columns
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                # Serialize Python list/dict to JSON string for JSONB columns
                processed_data[key] = json.dumps(value)
            else:
                processed_data[key] = value

        # Add update timestamp
        processed_data['upd_date'] = datetime.now()

        set_clause = ', '.join([f"{col} = %s" for col in processed_data.keys()])
        values = tuple(processed_data.values()) + (pk_value,)

        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE {self.pk_column} = %s AND delete_yn = 0
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, values)
            return cursor.rowcount > 0

    def delete(self, pk_value: int) -> bool:
        """
        Soft delete a record (set delete_yn = 1)

        Args:
            pk_value: Primary key value

        Returns:
            bool: True if deleted, False if not found
        """
        query = f"""
            UPDATE {self.table_name}
            SET delete_yn = 1, upd_date = %s
            WHERE {self.pk_column} = %s AND delete_yn = 0
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (datetime.now(), pk_value))
            return cursor.rowcount > 0

    def list(
        self,
        where: Optional[str] = None,
        params: Optional[tuple] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List records with optional filters

        Args:
            where: WHERE clause (e.g., "prompt_kind = %s")
            params: Parameters for WHERE clause
            order_by: ORDER BY clause (e.g., "cre_date DESC")
            limit: Maximum number of records

        Returns:
            List[Dict]: List of records
        """
        query = f"SELECT * FROM {self.table_name} WHERE delete_yn = 0"

        if where:
            query += f" AND {where}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        with get_db_cursor() as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results]

    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute custom SQL query

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            List[Dict]: Query results
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return [dict(row) for row in results]

    def execute_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Execute custom SQL query and return first result

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Optional[Dict]: First result or None
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return dict(result) if result else None
