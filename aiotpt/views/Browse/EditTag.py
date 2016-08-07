import re
from aiohttp import web
from .. import JsonEndpoint

class EditTagEndpoint(JsonEndpoint):

  RE_VALIDTAG = re.compile(r'[^a-zA-Z0-9\-]')

  async def get(self):
    self.assertAuth()
    req = self.request
    db = req["db"]

    editOption = self.sanitizeEnum(req.GET, "Op", "add", "delete")
    saveId = self.sanitizeNumber(req.GET, "ID", minimum=0)
    tagName = self.sanitizeString(req.GET, "Tag", minlen=4, maxlen=16,
      validator=lambda n: self.RE_VALIDTAG.search(n) == None)

    async with db.cursor() as cur:
      await cur.execute("""
        select exists(
          select 1 from Saves
          where id = %s
        ) as saveExists
      """, (saveId,))
      saveExists = (await cur.fetchone()).saveexists
      if not saveExists:
        raise self.exception(
          web.HTTPNotFound,
          "Save does not exist"
        )

      await cur.execute("""
        select exists(
          select 1 from TagRefs as tagref
          inner join Tags as tag
          on tag.id = tagref.tagID and tag.name = %s
          where saveID = %s
        ) as tagExists
      """, (tagName, saveId))
      tagExists = (await cur.fetchone()).tagexists

      await cur.execute("""
        select count(*) as tagCount from TagRefs tagref
        where tagref.saveId = %s
      """, (saveId,))
      tagCount = (await cur.fetchone()).tagcount

    if editOption == "add":
      if tagExists:
        raise self.exception(
          web.HTTPBadRequest,
          "Tag already exists"
        )
      if tagCount >= app["config"]["saves"]["tagLimit"]:
        raise self.exception(
          web.HTTPBadRequest,
          "Tag limit reached"
        )

      async with db.cursor() as cur:
        await cur.execute("""
          insert into Tags (name)
          values (%s)
          on conflict (name) do update
            set name=%s
          returning id
        """, (tagName, tagName))
        tagId = (await cur.fetchone()).id

        await cur.execute("""
          insert into TagRefs (
            saveId, userId, tagId, date, host
          ) values (
            %s, %s, %s, now(), %s
          )
        """, (
          saveId, req["user"].id, tagId, req["host"])
        )

        await cur.execute("""
          select name from Tags as tag
          inner join TagRefs as tagref
          on tagref.saveId = %s
        """, (saveId,))
        tagRows = await cur.fetchall()

        return self.response({
          "Tags": [row.name for row in tagRows]
        })

    elif editOption == "delete":
      if not tagExists:
        raise self.exception(
          web.HTTPBadRequest,
          "Tag does not exist"
        )

      async with db.cursor() as cur:
        await cur.execute("""
          select userId from Saves
          where id = %s
        """)
        userId = cur.fetchone().userid
        if userId != req["user"].id:
          raise self.exception(
            web.HTTPForbidden,
            "Not authorized to delete this tag"
          )

        await cur.execute("""
          delete from TagRefs as tagref
          inner join Tags as tag
          on tag.name = %s
          where tagref.saveId = %s
        """, (tagName, saveId))

        await cur.execute("""
          select name from Tags as tag
          inner join TagRefs as tagref
          on tagref.saveId = %s
        """, (saveId,))
        tagRows = await cur.fetchall()

        return self.response({
          "Tags": [row.name for row in tagRows]
        })
