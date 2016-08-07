from aiohttp import web
from . import JsonEndpoint

class UserEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    userName = self.sanitizeString(req.GET, "Name", required=False)
    userId = self.sanitizeNumber(req.GET, "ID", required=False, minimum=0)

    userRow = None

    if userName:
      async with db.cursor() as cur:
        await cur.execute("""
          select name, id,
            biography, location, website
          from Users
          where name like %s
        """, (userName,))
        userRow = await cur.fetchone()

    elif userId:
      async with db.cursor() as cur:
        await cur.execute("""
          select name, id,
            biography, location, website
          from Users
          where id = %s
        """, (userId,))
        userRow = await cur.fetchone()

    else:
      raise self.exception(web.HTTPBadRequest, "Name or ID missing")

    if userRow:
      async with db.cursor() as cur:
        await cur.execute("""
          select count(*) as saveCount from Saves
          where userId = %s
        """, (userId,))
        saveCount = (await cur.fetchone()).savecount

      return self.response({
        "User": {
          "Username": userRow.name,
          "ID": userRow.id,
          "Avatar": "http://powdertoy.co.uk/Design/Images/Avatar.png",
          "Age": 0,
          "Location": userRow.location,
          "Biography": userRow.biography,
          "Website": userRow.website,
          "Saves": {
            "Count": saveCount,
            # TODO
            "AverageScore": 0,
            "HighestScore": 0
          },
          "Forum": {
            "Topics": 0,
            "Replies": 0,
            "Reputation": 0
          }
        }
      })

    else:
      raise self.exception(web.HTTPNotFound, "User not found")
