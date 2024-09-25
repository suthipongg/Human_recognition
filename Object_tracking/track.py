import logging

from services.object_tracking_service import ObjectTrackingService
from services.redis_service import RedisClient

RedisClient.connecct()
if not RedisClient.check_redis_connection():
    RedisClient.clear_redis_data('frame')
    raise Exception("Redis connection failed")

logging.basicConfig(level = logging.INFO)
logging.info("tracking service initial")

track = ObjectTrackingService()
track.run_tracking()