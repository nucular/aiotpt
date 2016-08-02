from datetime import datetime
from aiohttp import web
from . import JsonEndpoint
from .. import utils
from ..config import config

class LoginEndpoint(JsonEndpoint):

  async def post(self):
    req = self.request
    db = req["db"]
    POST = await req.post()
    print(POST)

    userName = self.sanitizeString(POST, "Username")
    passwordHash = self.sanitizeString(POST, "Hash")

    async with db.cursor() as cur:
      await cur.execute("""
        select * from Users
        where name like %s and passwordHash = %s and status = 'ok'
      """, (userName, passwordHash))
      userRow = await cur.fetchone()

    if not userRow:
      raise self.exception(
        web.HTTPUnauthorized, "Username or Password incorrect")

    while True:
      sessionId = utils.generateRandomString(30)
      sessionKey = utils.generateRandomString(10)

      async with db.cursor() as cur:
        await cur.execute("""
          select exists(
            select 1 from Sessions
            where sessionId = %s or sessionKey = %s
          ) as exists
        """, (sessionId, sessionKey))
        if not (await cur.fetchone()).exists:
          break

    async with db.cursor() as cur:
      await cur.execute("""
        insert into Sessions (
          userId, sessionId, sessionKey, loginDate, host
        ) values (
          %s, %s, %s, %s, %s
        )
      """, (
        userRow.id,
        sessionId, sessionKey,
        datetime.now(), req["host"]
      ))

    return self.response({
      "UserID": userRow.id,
      "SessionID": sessionId,
      "SessionKey": sessionKey,
      "Elevation": userRow.elevation.title(),
      "Notifications": []
    })
