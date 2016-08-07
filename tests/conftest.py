import asyncio
import os, sys

import pytest
from aiohttp import web
from aiohttp.pytest_plugin import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(sys.modules[__name__].__file__), ".."))
from aiotpt.app import create_app

pytest_plugins = "aiohttp.pytest_plugin"

@pytest.yield_fixture
def test_client(loop):
  client = None

  @asyncio.coroutine
  def _create_from_app_factory(app_factory, *args, **kwargs):
    nonlocal client
    app = app_factory(loop, *args, **kwargs)
    client = TestClient(app)
    yield from app.on_startup.send()
    yield from client.start_server()
    return client

  yield _create_from_app_factory

  if client:
    client.close()


@pytest.fixture
def cli(loop, test_client):
  return loop.run_until_complete(test_client(create_app))
