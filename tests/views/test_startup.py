async def test_startup(cli):
  res = await cli.get("/Startup.json")
  assert res.status == 200
