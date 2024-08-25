import redis, json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import Config

# Create Redis client using ENV values
redis_client = redis.StrictRedis(**Config.REDIS_CLIENT)

def check_redis_connection():
    try:
        redis_client.ping()
        print("::: [\033[96mRedis\033[0m] connected \033[92msuccessfully\033[0m. :::")
        return True
    except Exception as e:
        print(f"\033[91mFailed\033[0m to connect to [\033[96mRedis\033[0m]: {e}")
        return False

def clear_redis_data(id):
    return redis_client.delete(id)

def set_redis_data(id, data):
    redis_client.set(id, json.dumps(data), ex=None)
    
def get_redis_data(id):
    cache_response = redis_client.get(id)
    data = json.loads(cache_response) if cache_response else None
    return data