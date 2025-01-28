from typing import Optional
import requests
from app.core.config import settings, logger
from app.utils.exceptions import RedisError

class RedisHandler:

    def __init__(self):
        self.base_url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        logger.info("✅ RedisHandler 초기화 완료")

    def set(self, key: str, value: str) -> bool:
        try:
            url = f"{self.base_url}/set/{key}/{value}"
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()  # 오류 발생 시 예외 처리
            logger.info(f"✅ Redis SET 저장 성공: {key} = {value}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 Redis SET 저장 실패: {e}")
            raise RedisError(message=f"Redis set failed", detail={"error": str(e)})

    def setex(self, key: str, value: str, ttl: int = 1200) -> bool:
        try:
            ttl = int(ttl)  # TTL이 정수인지 검증
            url = f"{self.base_url}/set/{key}/{value}?EX={ttl}"
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            logger.info(f"✅ Redis SETEX 저장 성공: {key} = {value}, TTL={ttl}")
            return True
        except (ValueError, requests.exceptions.RequestException) as e:
            logger.error(f"🚨 Redis SETEX 오류: {e}")
            raise RedisError(message=f"Redis store failed", detail={"error": str(e)})

    def get(self, key: str) -> Optional[str]:
        try:
            url = f"{self.base_url}/get/{key}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            result = response.json().get("result", None)

            if result:
                logger.info(f"🔹 Redis GET 요청 성공: {key} = {result}")
                return result
            else:
                logger.warning(f"⚠️ Redis GET 요청: {key} 값 없음")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 Redis GET 요청 실패: {e}")
            raise RedisError(f"Redis get failed", detail={"error": str(e)})

    def delete(self, key: str) -> bool:
        try:
            url = f"{self.base_url}/del/{key}"
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            logger.info(f"✅ Redis DELETE 성공: {key}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 Redis DELETE 실패: {e}")
            raise RedisError(f"Redis delete failed", detail={"error": str(e)})

redis_handler = RedisHandler()
