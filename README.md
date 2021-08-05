# timing-asgi-statsd
[![CircleCI](https://circleci.com/gh/nkonin/timing-asgi.svg?style=svg)](https://circleci.com/gh/nkonin/timing-asgi)
[![PyPI Downloads](https://img.shields.io/pypi/dm/timing-asgi-statsd.svg)](https://pypi.org/project/timing-asgi-statsd/)
[![PyPI Version](https://img.shields.io/pypi/v/timing-asgi-statsd.svg)](https://pypi.org/project/timing-asgi-statsd/)
[![License](https://img.shields.io/badge/license-mit-blue.svg)](https://pypi.org/project/timing-asgi-statsd/)

This is a timing middleware for [ASGI](https://asgi.readthedocs.org), useful for automatic instrumentation of ASGI endpoints.

This if fork of [timing-asgi](https://github.com/steinnes/timing-asgi). 
Key difference - pure statsd support (no tags) instead of [Datadog](https://www.datadoghq.com/).

# ASGI version

This middleware only supports ASGI3.

# installation

```
pip install timing-asgi-statsd
```

# usage


Here's an example using the Starlette ASGI framework which prints out the timing metrics..

A more realistic example which emits the timing metrics to Datadog can be found at
[https://github.com/steinnes/timing-starlette-asgi-example](https://github.com/steinnes/timing-starlette-asgi-example).


```python
import uvicorn

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from timing_asgi import TimingMiddleware, TimingClient
from timing_asgi.integrations import StarletteScopeToName


class PrintTimings(TimingClient):
    def timing(self, metric_name, timing, tags):
        print(metric_name, timing, tags)


app = Starlette()


@app.route("/")
def homepage(request):
    return PlainTextResponse("hello world")


app.add_middleware(
    TimingMiddleware,
    client=PrintTimings(),
    metric_namer=StarletteScopeToName(prefix="myapp", starlette_app=app)
)

if __name__ == "__main__":
    uvicorn.run(app)

```

Running this example and sending some requests:

```
$ python app.py
INFO: Started server process [35895]
INFO: Waiting for application startup.
2019-03-07 11:38:01 INFO  [timing_asgi.middleware:44] ASGI scope of type lifespan is not supported yet
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: ('127.0.0.1', 58668) - "GET / HTTP/1.1" 200
myapp.__main__.homepage 0.0006690025329589844
INFO: ('127.0.0.1', 58684) - "GET /asdf HTTP/1.1" 404
myapp.asdf 0.0005478858947753906
```
