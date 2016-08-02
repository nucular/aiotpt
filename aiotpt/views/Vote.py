from datetime import datetime
from aiohttp import web
from . import LegacyEndpoint
from ..config import config

class VoteEndpoint(LegacyEndpoint):

  async def post(self):
    self.assertAuth()
    req = self.request
    db = req["db"]

    saveId = self.sanitizeNumber(req.GET, "ID", minimum=0)
    voteDirection = self.sanitizeEnum(req.GET, "Action", "Up", "Down").lower()

    async with db.cursor() as cur:
      await cur.execute("""
        select * from Save
        where id = %s
      """, (saveId,))
      saveRow = await cur.fetchone()

    if not saveRow:
      raise self.exception(web.HTTPNotFound, "Save no longer exists")

    if saveRow.userid == req["user"].userid:
      raise self.exception(web.HTTPForbidden, "You cannot vote for yourself")

    async with db.cursor() as cur:
      await cur.execute("""
        select exists(
          select 1 from Vote
          where userId = %s and saveId = %s
        )
      """, (req["user"].userid, saveId))
      if await cur.fetchone():
        raise self.exception(web.HTTPForbidden, "You have already voted")

    async with db.cursor() as cur:
      await cur.execute("""
        insert into Votes (
          saveId, userId, direction, date, host
        ) values (
          %s, %s, %s, %s, %s
        )
      """, (
        saveId, req["user"].userid, voteDirection,
        datetime.now(), req["host"]
      ))
      if voteDirection == "up":
        await cur.execute("""
          update Save
          set score = score + %s
          set scoreUp = scoreUp + 1
          where saveId = %s
        """, (saveId))
      else:
        await cur.execute("""
          update Save
          set score = score - 1
          set scoreDown = scoreDown + 1
          where saveId = %s
        """, (saveId))

      return self.response("OK")
