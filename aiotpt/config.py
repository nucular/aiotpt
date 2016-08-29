import configparser
import datetime
import logging, logging.config
import os
import urllib.parse
from . import __version__

log = logging.getLogger(__name__)

logging.config.dictConfig({
  "version": 1,
  "disable_existing_loggers": False,
  "formatters": {
    "standard": {
      "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
      "datefmt": "%I:%M:%S"
    }
  },
  "handlers": {
    "default": {
      "level": "DEBUG",
      "formatter": "standard",
      "class": "logging.StreamHandler"
    }
  },
  "loggers": {
    "": {
      "handlers": ["default"],
      "level": "DEBUG",
      "propagate": True
    }
  }
})

urllib.parse.uses_netloc.append("postgres")
urllib.parse.uses_netloc.append("pg")

dburi = None
if "DATABASE_URL" in os.environ:
  dburi = urllib.parse.urlparse(os.environ["DATABASE_URL"])
  log.info("Loaded DBURI from $DATABASE_URL")
else:
  if os.path.isfile("sqitch.conf"):
    parser = configparser.ConfigParser()
    with open("sqitch.conf", "rt") as f:
      parser.read_file(f)
    if parser.has_option("engine \"pg\"", "target"):
      target = parser.get("engine \"pg\"", "target")
      log.debug("Sqitch target is %s", target)
      targetsection = "target \"{}\"".format(target)
      if parser.has_option(targetsection, "uri"):
        dburi = urllib.parse.urlparse(parser.get(targetsection, "uri")[3:])
        log.info("Loaded DBURI from sqitch.conf")

# Log the DBURI but redact the password
dburistr = dburi.geturl()
if dburi.password:
  dburistr = dburistr.replace(":" + dburi.password + "@", ":REDACTED@")
log.info("DBURI: %s", dburistr)

config = {
  "net": {
    "port": int(os.environ.get("PORT", 8080)),
    "hostname": os.environ.get("HOSTNAME", "localhost")
  },

  "database": {
    "database": dburi.path[1:],
    "user": dburi.username,
    "password": dburi.password,
    "host": dburi.hostname,
    "port": dburi.port,
    "maxsize": 20,
    "echo": True
  },

  "session": {
    "userIdHeader": "X-Auth-User-ID",
    "sessionIdHeader": "X-Auth-Session-Key",

    "maxAge": datetime.timedelta(30),
  },

  "saves": {
    "tagLimit": 10
  },

  "startup": {
    "updates": {
      "Stable": {
        "Major": 0,
        "Minor": 0,
        "Build": 0,
        "File": ""
      },
      "Beta": {
        "Major": 0,
        "Minor": 0,
        "Build": 0,
        "File": ""
      },
      "Snapshot": {
        "Major": 0,
        "Minor": 0,
        "Build": 0,
        "File": ""
      }
    },
    "motd": "aiotpt v{}".format(__version__)
  },

  "renderer": {
    "dir": os.path.join(os.path.dirname(__file__), "../renderer"),
    "executable": "Render",
    "async": False
  }
}
