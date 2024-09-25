import redis, json
import logging

from Configs.config import Config

class RedisClient:
    redis_client = None

    @classmethod
    def connecct(cls):
        cls.redis_client = redis.StrictRedis(**Config.REDIS_CLIENT)
        return cls.redis_client

    @classmethod
    def check_redis_connection(cls):
        try:
            cls.redis_client.ping()
            logging.info("::: [\033[96mRedis\033[0m] connected \033[92msuccessfully\033[0m. :::")
            return True
        except Exception as e:
            logging.info(f"\033[91mFailed\033[0m to connect to [\033[96mRedis\033[0m]: {e}")
            return False

    @classmethod
    def clear_redis_data(cls, id):
        return cls.redis_client.delete(id)

    @classmethod
    def set_redis_data(cls, id, data):
        cls.redis_client.set(id, json.dumps(data), ex=5/Config.FPS)
        
    @classmethod
    def get_redis_data(cls, id):
        cache_response = cls.redis_client.get(id)
        data = json.loads(cache_response) if cache_response else {}
        return data