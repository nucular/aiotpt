import argparse, asyncio, sys
from aiohttp import web
from .app import app
from .config import config

def num(type, min=None, max=None):
  def func(value):
    value = type(value)
    if min is not None and not (value > min):
      raise argparse.ArgumentTypeError(
        "{0} value must be more than {1} but is {2}".format(
          type.__name__, min, value
        )
      )
    if max is not None and not (value <= max):
      raise argparse.ArgumentTypeError(
        "{0} value must be at most {1} but is {2}".format(
          type.__name__, max, value
        )
      )
    return value
  func.__name__ = type.__name__
  return func


parser = argparse.ArgumentParser(
  description="Server for The Powder Toy written in Python"
)

parser.add_argument("--hostname", "-H",
  metavar="HOSTNAME",
  type=str,
  default=config["net"]["hostname"],
  help="""TCP/IP hostname to serve on (set to '{}')""".format(config["net"]["hostname"])
)

parser.add_argument("--port", "-P",
  metavar="PORT",
  type=num(int, min=0, max=65535),
  default=config["net"]["port"],
  help="""TCP/IP port to serve on (set to '{}')""".format(config["net"]["port"])
)

if __name__ == "__main__":
  args = parser.parse_args()
  loop = asyncio.get_event_loop()
  loop.run_until_complete(app.on_startup.send())
  web.run_app(app, host=args.hostname, port=args.port)
