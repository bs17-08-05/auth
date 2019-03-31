import asyncio

import aiopg

from configs import DSN


async def init_db(loop):
    db = await aiopg.create_pool(dsn=DSN, loop=loop)
    return db


async def close_db(app):
    app['db_pool'].close()
    await app['db_pool'].wait_closed()

