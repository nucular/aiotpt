from aiohttp import web
from . import JsonEndpoint
from ..config import config

class StartupEndpoint(JsonEndpoint):

  async def get(self):
    req = self.request
    db = req["db"]

    loggedIn = req["session"] is not None
    return self.response({
      "Updates": config["startup"]["updates"],
      "Notifications": [],
      "Session": loggedIn,
      "MessageOfTheDay": config["startup"]["motd"]
    })
