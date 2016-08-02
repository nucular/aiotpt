from aiohttp import web
from .. import JsonEndpoint
from ...config import config

class DeleteEndpoint(JsonEndpoint):

  async def get(self):
    self.assertAuth(level=2)
    req = self.request
    db = req["db"]

    saveId = self.sanitizeNumber(req.GET, "ID", minimum=0)
    mode = self.sanitizeEnum(req.GET, "Mode", "Unpublish", "Delete")

    if mode == "Unpublish":

      with db.cursor() as cur:
        await cur.execute("""
          select userId from Saves
          where id = %s and status = 'published'
        """, (saveId,))
        saveRow = await cur.fetchone()

      if not saveRow:
        raise self.exception(
          web.HTTPNotFound,
          "Save does not exist or is already private"
        )

      if (req["auth"] >= 2 and req["user"].id == saveRow.userid) \
        or req["user"].elevation == "moderator" \
        or req["user"].elevation == "administrator":
        with db.cursor() as cur:
          await cur.execute("""
            update Saves
            set status = 'unpublished'
            where id = %s
          """, (saveId,))
      else:
        raise self.exception(
          web.HTTPForbidden,
          "No permission to unpublish save"
        )

    elif mode == "Delete":

      with db.cursor() as cur:
        await cur.execute("""
          select userId from Saves
          where id = %s
        """, (saveId,))
        saveRow = await cur.fetchone()

      if not saveRow:
        raise self.exception(
          web.HTTPNotFound,
          "Save does not exist"
        )

      if (req["auth"] >= 2 and req["user"].id == saveRow.userid) \
        or req["user"].elevation == "moderator" \
        or req["user"].elevation == "administrator":
        with db.cursor() as cur:
          await cur.execute("""
            delete from Saves
            where id = %s
          """, (saveId,))
      else:
        raise self.exception(
          web.HTTPForbidden,
          "No permission to delete save"
        )

    return self.response({})
