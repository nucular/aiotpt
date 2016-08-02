import random, string

def generateRandomString(n, chars=None):
  return "".join(
    random.SystemRandom().choice(
      chars or (string.ascii_uppercase + string.digits)
    ) for _ in range(n)
  )

def truncateName(content, length=100, suffix="-"):
  if len(content) <= length:
    return content
  else:
    return " ".join(content[:length+1].split(" ")[0:-1]) + suffix
