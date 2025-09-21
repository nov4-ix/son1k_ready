from fastapi import Header, HTTPException, Depends
import time
import redis
from .settings import settings

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Simple rate-limit: X requests/min per userId (header X-User-Id)
def rate_limiter(limit:int=30):
    def dep(x_user_id: str = Header(default="anon")):
        key = f"rl:{x_user_id}:{int(time.time()//60)}"
        cnt = r.incr(key, 1)
        if cnt == 1:
            r.expire(key, 60)
        if cnt > limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return x_user_id
    return dep
