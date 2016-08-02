from aiohttp.errors import HttpMethodNotAllowed
from .config import config

async def sessionMiddleware(app, handler):
  async def middleware(req):
    db = req["db"]
    userIdHeader = config["session"]["userIdHeader"]
    sessionIdHeader = config["session"]["sessionIdHeader"]

    sessionKey = None
    userRow = None
    req["session"] = None
    req["user"] = None
    req["auth"] = 0

    if sessionIdHeader in req.headers:
      userId = req.headers.get(userIdHeader)
      sessionId = req.headers.get(sessionIdHeader)

      async with db.cursor() as cur:
        await cur.execute("""
          select * from Sessions
          where userId = %s and sessionId = %s
        """, (userId, sessionId))
        sessionRow = await cur.fetchone()

      async with db.cursor() as cur:
        await cur.execute("""
          select * from Users
          where id = %s and status = 'ok'
        """, (userId,))
        userRow = await cur.fetchone()

      if sessionRow and userRow:
        req["session"] = sessionRow
        req["user"] = userRow

        if "Key" in req.GET:
          if sessionRow.sessionkey == req.GET["Key"]:
            req["auth"] = 2
        else:
          req["auth"] = 1

    return await handler(req)

  return middleware
