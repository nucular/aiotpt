from aiohttp import web
from .. import JsonEndpoint
from ...config import config

class CommentsEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    saveId = self.sanitizeNumber(req.GET, "ID")
    searchStart = self.sanitizeNumber(req.GET, "Start", required=False,
      default=0, minimum=0)
    searchCount = self.sanitizeNumber(req.GET, "Count", required=False,
      default=20, minimum=1, maximum=100)

    async with db.cursor() as cur:
      await cur.execute("""
        select userId from Saves
        where id = %s
      """, (saveId,))
      if cur.rowcount == 0:
        return self.response([], status=404)
      saveAuthor = (await cur.fetchone()).userid

      await cur.execute("""
        select comment.userId,
          comment.saveId,
          comment.content,
          comment.date,
          author.name as username,
          author.elevation
        from Comments as comment

        left join Users as author
        on author.id = comment.userId

        where saveId = %s
        limit %s offset %s
      """, (saveId, searchCount, searchStart))
      commentRows = await cur.fetchall()

    searchResult = []
    for row in commentRows:
      if row.userid == saveAuthor:
        formattedUsername = "\bl" + row.username
      elif row.elevation == 'moderator':
        formattedUsername = "\bt" + row.username
      elif row.elevation == 'administrator':
        formattedUsername = "\bo" + row.username
      else:
        formattedUsername = row.username

      searchResult.append({
        "Username": row.username,
        "UserID": row.userid,
        "Gravatar": "http://powdertoy.co.uk/Design/Images/Avatar.png",
        "Text": row.content,
        "Timestamp": int(row.date.timestamp()),
        "FormattedUsername": formattedUsername
      })

    return self.response(searchResult)


  async def post(self):
    self.assertAuth()
    req = self.request
    db = req["db"]
    await req.post()

    saveId = self.sanitizeNumber(req.GET, "ID", minimum=0)
    comment = self.sanitizeString(req.POST, "Comment", maximum=1024)

    if len(comment) > 1024:
      return web.json_response({
        "Status": 0,
        "Error": "Comment must be 1024 characters or less!"
      }, status=400)

    async with db.cursor() as cur:
      await cur.execute("""
        insert into Comments (
          saveId, userId, date, content, host
        ) values (
          %s, %s, now(), %s, %s
        )
      """, (saveId, req["user"].id, comment, req["host"]))

    return self.response({
      "Status": 1
    })
