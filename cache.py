# cache.py
import redis
import json
from typing import Any, Optional, Type
from datetime import datetime, timedelta

class RedisCache:
    def __init__(self, redis_url: str, expiration_seconds: int = 300):
        self.redis = redis.from_url(redis_url)
        self.expiration_seconds = expiration_seconds

    def set(self, key: str, value: Any) -> None:
        serialized_value = json.dumps({
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        self.redis.setex(key, self.expiration_seconds, serialized_value)

    def get(self, key: str, model: Optional[Type[Any]] = None) -> Optional[Any]:
        data = self.redis.get(key)
        if not data:
            return None

        parsed_data = json.loads(data)
        timestamp = datetime.fromisoformat(parsed_data['timestamp'])
        if datetime.now() - timestamp > timedelta(seconds=self.expiration_seconds):
            self.redis.delete(key)
            return None
        
        value = parsed_data['value']
        return model.parse_obj(value) if model else value
