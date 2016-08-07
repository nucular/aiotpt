import asyncio, os, re
from datetime import datetime
from aiohttp import web
from . import LegacyEndpoint
from ..config import config

class SaveEndpoint(LegacyEndpoint):

  RE_VALIDNAME = re.compile(r'[^a-zA-Z0-9\-\s!.,\(\)]')

  async def post(self):
    self.assertAuth()
    req = self.request
    db = req["db"]
    await req.post()

    saveFileField = self.sanitize(req.POST, "Data")

    saveName = self.sanitizeString(req.POST, "Name", minlen=3, maxlen=50,
      validator=lambda n: self.RE_VALIDNAME.search(n) == None)
    saveDescription = self.sanitizeString(req.POST, "Description", minlen=5,
      maxlen=255)
    savePublish = self.sanitizeEnum(req.POST, "Publish", "Public", "Private")

    saveName = " ".join(saveName.split(" "))
    saveDescription = " ".join(saveDescription.split(" "))

    saveId = None
    async with db.cursor() as cur:
      await cur.execute("""
        select id from Saves
        where userId = %s and name = %s
        and (status = 'published' or status = 'unpublished')
      """, (req["user"].id, saveName))
      result = (await cur.fetchone())
      if result:
        saveId = result.id

    rendererDir = app["config"]["renderer"]["dir"]
    rendererExecutable = app["config"]["renderer"]["executable"]

    saveData = saveFileField.file.read()
    saveFilePath = os.path.join(rendererDir, "save.cps")
    with open(saveFilePath, "wb") as f:
      f.write(saveData)

    if app["config"]["renderer"]["async"]:
      process = await asyncio.create_subprocess_exec(
        os.path.join(rendererDir, rendererExecutable),
        saveFilePath, os.path.join(rendererDir, "preview")
      )
      await process.wait()
    else:
      import subprocess
      subprocess.run([
        os.path.join(rendererDir, rendererExecutable),
        saveFilePath, os.path.join(rendererDir, "preview")
      ])

    with open(os.path.join(rendererDir, "preview.png"), "rb") as f:
      previewPng = f.read()
    with open(os.path.join(rendererDir, "preview-small.png"), "rb") as f:
      previewPngSmall = f.read()
    with open(os.path.join(rendererDir, "preview.pti"), "rb") as f:
      previewPti = f.read()
    with open(os.path.join(rendererDir, "preview-small.pti"), "rb") as f:
      previewPtiSmall = f.read()

    currDate = datetime.now()

    async with db.cursor() as cur:
      if saveId == None: # Save is new
        await cur.execute("""
          insert into Saves (
            userId, name, description,
            dateCreated, dateChanged,
            saveData, previewPng, previewPngSmall, previewPti, previewPtiSmall,
            host
          ) values (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s
          )
          returning id as saveId
        """, (
          req["user"].id, saveName, saveDescription, currDate, currDate,
          saveData, previewPng, previewPngSmall, previewPti, previewPtiSmall,
          req["host"]
        ))
        saveId = (await cur.fetchone()).saveid
      else: # Save is being reuploaded
        await cur.execute("""
          update Saves
          set name = %s, description = %s,
            dateChanged = %s,
            saveData = %s,
            previewPng = %s, previewPngSmall = %s,
            previewPti = %s, previewPtiSmall = %s,
            host = %s
          where id = %s
        """, (
          saveName, saveDescription, currDate,
          saveData, previewPng, previewPngSmall, previewPti, previewPtiSmall,
          req["host"],
          saveId
        ))

    return self.response("OK, {}".format(saveId))
