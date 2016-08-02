# aiotpt

This is an implementation of a server for the falling sand game
[The Powder Toy](http://powdertoy.co.uk), written in
[Python](https://python.org) using [aiohttp](http://aiohttp.readthedocs.io) for
asynchronous HTTP and [PostgreSQL](https://www.postgresql.org) for data
storage.

Due to various bugs in the client code of TPT, this server is currently only
compatible with recent revisions of it (starting at commit
[9a855cc](https://github.com/simtr/The-Powder-Toy/commit/9a855cc8cb01e2db3691f4c40b26457da31fdc47)
to be accurate).

This project is still in its infancy and can **not** be considered stable or
secure by any means. If you make an instance of it open to the public, Ristovski
will probably hack you.

## Installing

- Install [Python 3.5+](https://python.org)
- Install [PostgreSQL 9.5+](https://www.postgresql.org)
- Build the save renderer from [source](https://github.com/simtr/The-Powder-Toy)
  using `--renderer` and move the `Render` executable into `renderer/`
- Build The Powder Toy from a modified source (change SERVER and STATICSERVER in
  `src/Config.h` to `localhost:8080` or whatever)
- `pip install -r requirements.txt`
- `set DATABASE=postgres://user@host:port/database`
- `psql -f schema.sql`
- `python -m aiotpt`

## Todo

- Proper unit testing using [pytest](http://pytest.org)
- Allow static storage of saves instead of storing them inside the database
- Inline documentation
- Static HTML frontend/website
- High-level moderation/administration tools
- Basic analytics and cheat protection
