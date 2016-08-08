import asyncio
import logging
import os.path

from aiohttp import web, signals
from aiohttp_index import IndexMiddleware
import aiopg
from psycopg2.extras import NamedTupleCursor

from .config import config
from .session import sessionMiddleware
from .prep import prepareMiddleware
from .routes import routes

log = logging.getLogger(__name__)

def create_app(loop=None):
  app = web.Application(
    loop=loop or asyncio.get_event_loop(),
    middlewares=[
      prepareMiddleware,
      sessionMiddleware,
      IndexMiddleware()
    ]
  )
  app.on_startup = signals.Signal(app)

  log.debug(config)
  app["config"] = config

  async def on_startup():
    for r in routes:
      app.router.add_route(r[0], r[1], r[2])
    app.router.add_static("/", os.path.join(os.path.dirname(__file__), "../static"))

    pool = await aiopg.create_pool(
      loop=app.loop,
      cursor_factory=NamedTupleCursor,
      **config["database"]
    )
    app["pool"] = pool
  app.on_startup.append(on_startup)

  return app
