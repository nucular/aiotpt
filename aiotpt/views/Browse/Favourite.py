import re
from aiohttp import web
from .. import JsonEndpoint

class FavouriteEndpoint(JsonEndpoint):

  async def get(self):
    self.assertAuth()
    req = self.request
    db = req["db"]

    saveId = self.sanitizeNumber(req.GET, "ID", minimum=0)
    mode = self.sanitizeEnum(req.GET, "Mode", "Add", "Remove",
      required=False, default="Add")

    async with db.cursor() as cur:
      await cur.execute("""
        select exists(
          select 1 from Saves
          where id = %s
        ) as saveExists
      """, (saveId,))
      saveExists =  (await cur.fetchone()).saveexists
      if not saveExists:
        raise self.exception(
          web.HTTPNotFound,
          "Save does not exist"
        )

      if mode == "Add":
        await cur.execute("""
          insert into FavouriteRefs (
            userId, saveId
          ) values (
            %s, %s
          ) on conflict do nothing
        """, (req["user"].id, saveId))

      elif mode == "Remove":
        await cur.execute("""
          remove from FavouriteRefs
          where userId = %s and saveId = %s
        """, (req["user"].id, saveId))

    return self.response({})
