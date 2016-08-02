from datetime import datetime
import re
from aiohttp import web
from .. import JsonEndpoint
from ...config import config
from ... import utils

class BrowseEndpoint(JsonEndpoint):

  RE_SORTQUERY = re.compile(r'\bsort\:(\w+)\b')
  RE_USERQUERY = re.compile(r'\b(?:by|user)\:([^a-zA-Z0-9\-_]+)\b')
  RE_IDQUERY = re.compile(r'\b(?:id|history)\:(\d+)\b')
  RE_ORDERQUERY = re.compile(r'\border:(asc|desc)\b')

  async def get(self):
    req = self.request
    db = req["db"]

    searchStart = self.sanitizeNumber(req.GET, "Start", required=False,
      default=0, minimum=0)
    searchCount = self.sanitizeNumber(req.GET, "Count", required=False,
      default=20, minimum=1, maximum=100)
    searchQuery = self.sanitizeString(req.GET, "Search_Query", required=False,
      default="", empty=True, maxlen=255)
    searchCategory = self.sanitizeString(req.GET, "Category", required=False,
      default="", empty=True, maxlen=255)

    searchSort = None
    m = self.RE_SORTQUERY.search(searchQuery)
    if m:
      searchSort = m.group(1)
      searchQuery = searchQuery[:m.start()] + searchQuery[m.end():]

    searchOrder = None
    m = self.RE_ORDERQUERY.search(searchQuery)
    if m:
      searchOrder = m.group(1)
      searchQuery = searchQuery[:m.start()] + searchQuery[m.end():]

    searchByUser = None
    m = self.RE_USERQUERY.match(searchCategory)
    if m:
      searchByUser = m.group(1)
      searchCategory = searchCategory[:m.start()] + searchCategory[m.end():]

    m = self.RE_USERQUERY.search(searchQuery)
    if m:
      searchByUser = m.group(1)
      searchQuery = searchQuery[:m.start()] + searchQuery[m.end():]

    searchById = None
    m = self.RE_IDQUERY.search(searchQuery)
    if m:
      searchById = m.group(1)
      searchQuery = searchQuery[:m.start()] + searchQuery[m.end():]

    query = """
      select save.id,
        save.dateCreated, save.dateChanged,
        save.score, save.scoreUp, save.scoreDown,
        save.name, save.status,
        author.name as userName,
        comment.commentCount
      from Saves as save
    """
    params = []

    if searchCategory == "Favourites":
      query += """
        inner join FavouriteRefs as ref
        on ref.userId = %s and ref.saveId = save.id
      """
      params.append(req["user"].id if req["user"] else None)
      searchSort = searchSort or "id"
      searchOrder = searchOrder or "asc"

    if searchByUser:
      query += """
        inner join Users as author
        on author.id = save.userId and author.name == %s
      """
      params.append(searchByUser)
    else:
      query += """
        left join Users as author
        on author.id = save.userId
      """

    query += """
      left join (
        select saveId, count(*) as commentCount
        from Comments
        group by saveId
      ) comment
      on comment.saveId = save.id

      where (
        save.status = 'published'
        or (save.status = 'unpublished' and save.userId = %s)
      )
    """
    params.append(req["user"].id if req["user"] else None)

    if searchById:
      query += " and save.id = %s"
      params.append(searchById)

    searchTokens = searchQuery.split()
    if len(searchTokens) > 0:
      query += "and (" + " or ".join([
        "lower(save.name) like %s"
        for token in searchTokens
      ]) + ")"
      params += ["%" + token.lower() + "%" for token in searchTokens]

    searchSort = searchSort or "id"
    searchOrder = searchOrder or "desc"

    query += "order by " + {
      "date": "save.dateChanged",
      "score": "save.score",
      "id": "save.id",
      "views": "save.views"
    }.get(searchSort, "date") \
      + " " + searchOrder + " limit %s offset %s"
    params.append(searchCount)
    params.append(searchStart)

    async with db.cursor() as cur:
      await cur.execute(query, params)
      saveRows = await cur.fetchall()

    return self.response({
      "Count": cur.rowcount,
      "Saves": [{
        "ID": row.id,
        "Created": int(row.datecreated.timestamp()),
        "Updated": int(row.datechanged.timestamp()),
        "Version": 0,
        "Score": row.score,
        "ScoreUp": row.scoreup,
        "ScoreDown": row.scoredown,
        "Name": row.name,
        "ShortName": utils.truncateName(row.name, 20),
        "Username": row.username,
        "Comments": row.commentcount or 0,
        "Published": row.status == "published"
      } for row in saveRows]
    }, status=None)
