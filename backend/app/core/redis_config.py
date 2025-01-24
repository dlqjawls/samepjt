# app/core/redis_config.py
import requests
from app.core.config import settings, logger  # ✅ config.py에서 설정 가져옴

class UpstashRedisClient:
    def __init__(self):
        self.base_url = settings.UPSTASH_REDIS_REST_URL
        self.token = settings.UPSTASH_REDIS_REST_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def set(self, key, value):
        """Redis SET 저장"""
        url = f"{self.base_url}/set/{key}/{value}"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            logger.info(f"✅ Redis SET 저장 성공: {key} = {value}")
        else:
            logger.error(f"🚨 Redis SET 저장 실패: {response.json()}")

        return response.json()

    def setex(self, key, value, ttl):
        """Redis SETEX 저장 (TTL 적용)"""
        try:
            ttl = int(ttl)  # ✅ TTL이 정수인지 확인
            url = f"{self.base_url}/set/{key}/{value}?EX={ttl}"
            response = requests.post(url, headers=self.headers)

            if response.status_code == 200:
                logger.info(f"✅ Redis SETEX 저장 성공: {key} = {value}, TTL={ttl}")
            else:
                logger.error(f"🚨 Redis SETEX 저장 실패: {response.json()}")

            return response.json()
        except ValueError as e:
            logger.error(f"🚨 Redis SETEX 오류 (TTL 변환 실패): {e}")
            return {"error": "Invalid TTL value"}

    def get(self, key):
        """Redis GET 요청"""
        url = f"{self.base_url}/get/{key}"
        response = requests.get(url, headers=self.headers)
        result = response.json().get("result", None)

        if result:
            logger.info(f"🔹 Redis GET 요청 성공: {key} = {result}")
        else:
            logger.warning(f"⚠️ Redis GET 요청: {key} 값 없음")

        return result

    def delete(self, key):
        """Redis DELETE 요청"""
        url = f"{self.base_url}/del/{key}"
        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            logger.info(f"✅ Redis DELETE 성공: {key}")
        else:
            logger.error(f"🚨 Redis DELETE 실패: {response.json()}")

        return response.json()

def redis_config():
    """Redis 클라이언트 초기화"""
    try:
        logger.info("🔹 Upstash Redis 클라이언트 초기화 중...")
        return UpstashRedisClient()
    except Exception as e:
        logger.error(f"🚨 Redis 초기화 실패: {e}")
        return None
