from aiohttp import web
from . import JsonEndpoint
from ..config import config

class StatsEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    async with db.cursor() as cur:
      await cur.execute("""
        select reltuples as userCount from pg_class
        where relname = 'users'
      """)
      userCount = int((await cur.fetchone()).usercount)
      await cur.execute("""
        select reltuples as saveCount from pg_class
        where relname = 'saves'
      """)
      saveCount = int((await cur.fetchone()).savecount)

    return self.response({
      "UserCount": userCount,
      "SaveCount": saveCount
    })
