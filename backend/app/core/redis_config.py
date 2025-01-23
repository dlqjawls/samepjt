import os
from dotenv import load_dotenv
import requests

load_dotenv()

class UpstashRedisClient:
    def __init__(self):
        self.base_url = os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def set(self, key, value):
        """ 기본적인 SET 저장 """
        url = f"{self.base_url}/set/{key}/{value}"
        response = requests.post(url, headers=self.headers)
        return response.json()

    def setex(self, key, value, ttl):
        """ TTL 적용하여 Redis에 저장 """
        url = f"{self.base_url}/set/{key}/{value}?EX={ttl}"
        response = requests.post(url, headers=self.headers)
        return response.json()

    def get(self, key):
        """ Redis에서 값 가져오기 """
        url = f"{self.base_url}/get/{key}"
        response = requests.get(url, headers=self.headers)
        return response.json().get("result", None)  # 값이 없으면 None 반환

    def delete(self, key):
        """ Redis에서 키 삭제 """
        url = f"{self.base_url}/del/{key}"
        response = requests.post(url, headers=self.headers)
        return response.json()

def redis_config():
    try:
        return UpstashRedisClient()
    except Exception as e:
        print(f"Redis connection failure: {e}")
        return None
