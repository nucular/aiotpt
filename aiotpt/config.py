import datetime, os, urllib.parse
import logging.config
from . import __version__

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ.get("DATABASE_URL",
  "postgres://postgres@localhost:5432/postgres"))

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

config = {
  "net": {
    "port": int(os.environ.get("PORT", 8080)),
    "hostname": os.environ.get("HOSTNAME", "localhost")
  },

  "database": {
    "database": url.path[1:],
    "user": url.username,
    "password": url.password,
    "host": url.hostname,
    "port": url.port,
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
