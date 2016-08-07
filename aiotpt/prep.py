async def prepareMiddleware(app, handler):
  async def middleware(req):
    # Get peer information
    peername = req.transport.get_extra_info("peername")
    if peername is not None:
      req["host"] = peername[0]

    # Fetch a database connection from the pool
    async with app["pool"].acquire() as conn:
      req["db"] = conn
      try:
        res = await handler(req)
      except Exception as e:
        print(e)
        raise e

    return res

  return middleware
