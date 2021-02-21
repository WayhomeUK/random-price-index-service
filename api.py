import os
import structlog
import aioredis
from aiohttp import web, helpers

logger = structlog.get_logger()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASS = os.getenv('REDIS_PASS', None)
APP_PASSWORD = os.getenv('APP_PASSWORD', None)


async def wrpi(request):
    error_response = web.json_response({
        'error': 'please authenticate to use this API',
        'error_code': 'forbidden',
    }, status=401, headers={
        'WWW-Authenticate': 'Basic realm="wayhome wpri"',
    })
    try:
        auth = helpers.BasicAuth.decode(
                request.headers.get('authorization', ''))
    except ValueError as e:
        logger.debug('invalid auth header', exc_info=e)
        return error_response
    if auth.password != APP_PASSWORD:
        logger.debug('invalid password', password=auth.password)
        return error_response
    value = await request.app['redis'].get('wrpi-latest')
    timestamp = await request.app['redis'].get('wrpi-timestamp')
    return web.json_response({
        'latest_value': float(value.decode()),
        'latest_calculation_at': timestamp.decode(),
    })


async def redis_up(app):
    logger.info(
        'connecting to redis', host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    app['redis'] = await aioredis.create_redis_pool(
        (REDIS_HOST, REDIS_PORT),
        db=REDIS_DB,
        password=REDIS_PASS,
    )
    logger.info('redis connected')


async def redis_down(app):
    logger.info('closing redis connection pool')
    app['redis'].close()
    await app['redis'].wait_closed()
    logger.info('redis pool closed')


if __name__ == '__main__':
    structlog.configure(processors=[structlog.processors.JSONRenderer()])

    app = web.Application()
    app.router.add_get('/v0/wrpi', wrpi)
    app.on_startup.append(redis_up)
    app.on_cleanup.append(redis_down)
    web.run_app(app)
