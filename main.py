import asyncio

import aiohttp
import aiohttp_cors

from configs import HOST, PORT
from redis_manager import init_redis, close_redis
from db_manager import init_db, close_db
from routes import *


async def init(loop):
    # init app
    app = aiohttp.web.Application(loop=loop)

    # create redis connection
    redis_pool = await init_redis(loop)
    app['redis_pool'] = redis_pool
    app.on_cleanup.append(close_redis)

    db_pool = await init_db(loop)
    app['db_pool'] = db_pool
    app.on_cleanup.append(close_db)

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    setup_routes(app, cors)

    return app


def main():
    loop = asyncio.get_event_loop()

    app = loop.run_until_complete(init(loop))

    aiohttp.web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
