import re
from aiohttp import web
from .. import JsonEndpoint

class TagsEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    searchStart = self.sanitizeNumber(req.GET, "Start", required=False,
      default=0, minimum=0)
    searchCount = self.sanitizeNumber(req.GET, "Count", required=False,
      default=50, minimum=1, maximum=100)

    async with db.cursor() as cur:
      await cur.execute("""
        select reltuples as tagTotal from pg_class
        where relname = 'tags'
      """)
      tagTotal = (await cur.fetchone()).tagtotal

      await cur.execute("""
        select tag.name, tagCount from Tags as tag
        inner join (
          select tagId, count(*) as tagCount
          from TagRefs
          group by tagId
        ) as tagref
        on tag.id = tagref.tagId
        order by tagCount desc
        limit %s offset %s
      """, (searchCount, searchStart))
      tagRows = await cur.fetchall()

    return self.response({
      "TagTotal": int(tagTotal),
      "Results": len(tagRows),
      "Tags": [
        {
          "Count": row.tagcount,
          "Tag": row.name,
          "Restricted": "0"
        } for row in tagRows
      ]
    })
