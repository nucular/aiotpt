import re, os.path
from aiohttp import web
from . import SimpleEndpoint
from ..config import config

class StaticEndpoint(SimpleEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    saveId = self.sanitizeNumber(req.match_info, "id", minimum=0)
    fileExt = self.sanitizeEnum(req.match_info, "ext", "cps", "png", "pti")
    _, fileName = os.path.split(req.path)
    if fileExt == "png" or fileExt == "pti":
      imageSize = self.sanitizeEnum(req.match_info, "size", "small", "large")

    colName = None
    fileType = "text/plain" # XXX: horrible
    if fileExt == "cps":
      fileType = "application/vnd.powdertoy.save"
      colName = "saveData"
    elif fileExt == "png":
      fileType = "image/png"
      if imageSize == "small":
        colName = "previewPngSmall"
      else:
        colName = "previewPng"
    elif fileExt == "pti":
      fileType = "application/vnd.powdertoy.image"
      if imageSize == "small":
        colName = "previewPtiSmall"
      else:
        colName = "previewPti"

    async with db.cursor() as cur:
      await cur.execute("""
        select {} from Saves
        where id = %s
      """.format(colName), (saveId,))
      data = (await cur.fetchone())[0]

    # XXX: Due to a bug in aiohttp we are forced to convert the memoryview into
    # a bytes object when using StreamResponse. Might as well use Response then.
    # https://github.com/KeepSafe/aiohttp/blob/master/aiohttp/protocol.py#L701
    return web.Response(body=bytes(data), content_type="text/plain", headers={
      "Content-Description": "File Transfer",
      "Content-Disposition": "attachment; filename={}".format(fileName),
      "Expires": "0",
      "Cache-Control": "must-revalidate",
      "Pragma": "public"
    })
