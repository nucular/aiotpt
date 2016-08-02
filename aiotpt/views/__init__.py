import json
from aiohttp import web

class AbstractEndpoint(web.View):

  def response(self, data):
    raise NotImplementedError()

  def exception(self, exception, reason):
    raise NotImplementedError()

  def assertAuth(self, level=1):
    if self.request["auth"] < level:
      raise self.exception(web.HTTPUnauthorized, "Not Authorized")

  def sanitize(self, source, name, required=True, default=None,
    transformer=None, validator=None):
    if not name in source:
      if required:
        raise self.exception(web.HTTPBadRequest, "{} missing".format(name))
      else:
        data = default
    else:
      data = source[name]
    if transformer: data = transformer(data)
    if validator and not validator(data):
      raise self.exception(web.HTTPBadRequest, "{} invalid".format(name))
    return data

  def sanitizeEnum(self, source, name, *args, **kwargs):
    data = self.sanitize(source, name, **kwargs)
    if not name in source:
      return data
    if not data in args:
      raise self.exception(
        web.HTTPBadRequest,
        "{} must be {}".format(name, " or ".join(args))
      )
    return data

  def sanitizeString(self, source, name, empty=False, minlen=None,
    maxlen=None, **kwargs):
    data = self.sanitize(source, name, **kwargs)
    if not name in source:
      return data
    if not empty and len(data) == 0:
      raise self.exception(
        web.HTTPBadRequest,
        "{} may not be empty".format(name)
      )
    if (minlen and len(data) < minlen) or (maxlen and len(data) > maxlen):
      if minlen and maxlen:
        if minlen == maxlen:
          reason = "{} must be exactly {} characters".format(name, minlen)
        else:
          reason = "{} must be between {} and {} characters".format(name, minlen, maxlen)
      elif minlen:
        reason = "{} must be {} characters or above".format(name, minlen)
      elif maxlen:
        reason = "{} must be {} characters or below".format(name, maxlen)
      raise self.exception(web.HTTPBadRequest, reason)
    return data

  def sanitizeNumber(self, source, name, numtype=int, minimum=None,
    maximum=None, **kwargs):
    data = self.sanitize(source, name, **kwargs)
    if not name in source:
      return data
    try:
      data = numtype(data)
    except ValueError:
      raise self.exception(
        web.HTTPBadRequest,
        "{} must be a valid {} number".format(name, numtype)
      )
    if (minimum and data < minimum) or (maximum and data > maximum):
      if minimum and maximum:
        reason = "{} must be between {} and {}".format(name, minimum, maximum)
      elif minimum:
        reason = "{} must be above {}".format(name, minimum)
      elif maximum:
        reason = "{} must be below {}".format(name, maximum)
      raise self.exception(web.HTTPBadRequest, reason)
    return data


class SimpleEndpoint(AbstractEndpoint):

  def response(self, *args, **kwargs):
    return web.Response(*args, **kwargs)

  def exception(self, exception, reason, *args, **kwargs):
    return exception(reason=reason, *args, **kwargs)


class JsonEndpoint(AbstractEndpoint):

  def response(self, data, *args, status=1, **kwargs):
    if status and type(data) == dict and not "Status" in data:
      data["Status"] = status
    return web.json_response(data, *args, **kwargs)

  def exception(self, exception, reason, status=0, *args, **kwargs):
    text = json.dumps({
      "Status": status,
      "Error": reason
    })
    return exception(text=text, content_type="application/json", *args, **kwargs)


class LegacyEndpoint(AbstractEndpoint):

  def response(self, text, *args, **kwargs):
    return web.Response(text=text, content_type="text/plain", *args, **kwargs)

  def exception(self, exception, reason, *args, **kwargs):
    return exception(text=reason, content_type="text/plain", *args, **kwargs)
