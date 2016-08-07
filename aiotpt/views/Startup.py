from aiohttp import web
from . import JsonEndpoint

class StartupEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    loggedIn = req["session"] is not None
    return self.response({
      "Updates": req.app["config"]["startup"]["updates"],
      "Notifications": [],
      "Session": loggedIn,
      "MessageOfTheDay": req.app["config"]["startup"]["motd"]
    })
