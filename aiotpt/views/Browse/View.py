import re
from aiohttp import web
from .. import JsonEndpoint
from ... import utils

class ViewEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    saveId = self.sanitizeNumber(req.GET, "ID", minimum=0)

    async with db.cursor() as cur:
      await cur.execute("""
        update Saves
        set views = views + 1
        where id = %s
        returning id, userId,
          score, scoreDown, scoreUp, views,
          name, description,
          dateCreated, dateChanged,
          status
      """, (saveId,))
      saveRow = await cur.fetchone()

      if not saveRow:
        raise self.exception(
          web.HTTPNotFound,
          {
            "ID": 404,
            "Score":404,
            "ShortName": "Save doesn't exist",
            "Name": "Save doesn't exist",
            "Username": "FourOhFour",
            "Comments":404
          }
        )

      userName = None
      await cur.execute("""
        select name from Users
        where id = %s
      """, (saveRow.userid,))
      userRow = await cur.fetchone()
      if userRow:
        userName = userRow.name

      await cur.execute("""
        select count(*) as commentCount from Comments
        where saveId = %s
      """, (saveId,))
      commentCount = (await cur.fetchone()).commentcount

      if req["user"]:
        await cur.execute("""
          select exists(
            select 1 from FavouriteRefs
            where saveId = %s and userId = %s
          ) as isFavourite
        """, (saveId, req["user"].id))
        isFavourite = (await cur.fetchone()).isfavourite
      else:
        isFavourite = False

      await cur.execute("""
        select tag.name from Tags as tag
        inner join TagRefs as tagref
        on tagref.tagId = tag.id and tagref.saveId = %s
      """, (saveId,))
      tagRows = await cur.fetchall()

    return self.response({
      "ID": saveId,
      "Favourite": isFavourite,
      "Score": saveRow.score,
      "ScoreUp": saveRow.scoreup,
      "ScoreDown": saveRow.scoredown,
      "Views": saveRow.views,
      "ShortName": utils.truncateName(saveRow.name, 20),
      "Name": saveRow.name,
      "Description": saveRow.description,
      "DateCreated": int(saveRow.datecreated.timestamp()),
      "Date": int(saveRow.datechanged.timestamp()),
      "Username": userName,
      "Comments": commentCount,
      "Published": saveRow.status == "published",
      "Version": 0,
      "Tags": [
        row.name for row in tagRows
      ]
    })
