import os.path

from aiohttp import web, signals
from aiohttp_index import IndexMiddleware
import aiopg
from psycopg2.extras import NamedTupleCursor

from .config import config
from .session import sessionMiddleware
from .prep import prepareMiddleware
from .routes import routes

app = web.Application(
  middlewares=[
    prepareMiddleware,
    sessionMiddleware,
    IndexMiddleware()
  ]
)
app.on_startup = signals.Signal(app)

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
