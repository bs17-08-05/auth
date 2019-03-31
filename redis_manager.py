import asyncio

import aioredis

from configs import REDIS_HOST


async def init_redis(loop):
    redis = await aioredis.create_redis_pool(
            REDIS_HOST,
            minsize=5, maxsize=10,
            loop=loop)

    return redis


async def close_redis(app):
    app['redis_pool'].close()
    await app['redis_pool'].wait_closed()

