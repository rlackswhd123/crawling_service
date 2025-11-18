"""Idempotency Cache with Redis"""
import json
from typing import Optional
import redis.asyncio as redis
from app.config import settings


class IdempotencyCache:
    """Redis 기반 Idempotency 캐시"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = settings.redis_cache_ttl
        
    async def connect(self):
        """Redis 연결"""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    def _make_key(self, idempotency_key: str) -> str:
        """캐시 키 생성"""
        return f"ocr:idempotency:{idempotency_key}"
    
    async def get(self, idempotency_key: str) -> Optional[dict]:
        """
        캐시된 결과 조회
        
        Args:
            idempotency_key: Idempotency 키
            
        Returns:
            캐시된 OCR 결과 또는 None
        """
        if not self.redis_client:
            await self.connect()
        
        key = self._make_key(idempotency_key)
        cached = await self.redis_client.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    async def set(self, idempotency_key: str, result: dict):
        """
        결과 캐싱
        
        Args:
            idempotency_key: Idempotency 키
            result: OCR 결과
        """
        if not self.redis_client:
            await self.connect()
        
        key = self._make_key(idempotency_key)
        await self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(result, ensure_ascii=False)
        )


# 전역 캐시 인스턴스
idempotency_cache = IdempotencyCache()

