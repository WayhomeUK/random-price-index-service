import os
import random
import datetime
import structlog
import redis

logger = structlog.getLogger()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASS = os.getenv('REDIS_PASS', None)

if __name__ == '__main__':
    structlog.configure(processors=[structlog.processors.JSONRenderer()])
    logger.info(
        'connecting to redis', host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASS,
    )
    logger.info('redis connected!')

    value = random.randint(1, 1000000) / 10000
    timestamp = datetime.datetime.utcnow().isoformat()
    logger.info('new WRPI generated', value=value, calculated_at=timestamp)
    r.set('wrpi-latest', str(value))
    r.set('wrpi-timestamp', timestamp)
    logger.info('redis updated')
