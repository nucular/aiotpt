from hashlib import md5
import re
from aiohttp import web
from . import JsonEndpoint
from ..config import config

class RegisterEndpoint(JsonEndpoint):

  RE_VALIDNAME = re.compile(r'[^a-zA-Z0-9\-_]')

  async def post(self):
    req = self.request
    db = req["db"]
    await req.post()

    userName = self.sanitizeString(req.POST, "Username", minlen=3, maxlen=20,
      validator=lambda n: self.RE_VALIDNAME.search(n) == None)
    email = self.sanitizeString(req.POST, "Email", minlen=3, maxlen=255)
    # I believe these password requirements are sane
    password = self.sanitizeString(req.POST, "Password", minlen=3, maxlen=255)

    async with db.cursor() as cur:
      await cur.execute("""
        select exists(
          select 1 from Users
          where name like %s
        ) as exists
      """, (userName,))
      if (await cur.fetchone()).exists:
        raise self.exception(web.HTTPBadRequest, "Username already taken")

    passwordHash = md5(
      "{}-{}".format(
        userName,
        md5(password.encode()).hexdigest()
      ).encode()
    ).hexdigest()

    async with db.cursor() as cur:
      await cur.execute("""
        insert into Users (
          name, passwordHash, email, dateRegistered
        ) values (
          %s, %s, %s, now()
        )
      """, (
        userName, passwordHash, email
      ))

    return self.response({})
