import alog

from .utils import PathToName, TimingStats


class TimingMiddleware:
    """Timing middleware for ASGI applications

    Args:
      app (ASGI application): ASGI application
      client (TimingClient): the client used to emit instrumentation metrics
      metric_namer (MetricNamer): the callable used to construct metric names from the ASGI scope
    """

    def __init__(self, app, client, metric_namer=None):
        if metric_namer is None:
            metric_namer = PathToName(prefix="unnamed")

        self.app = app
        self.client = self.ensure_compliance(client)
        self.metric_namer = metric_namer

    def ensure_compliance(self, client):
        assert hasattr(client, "timing")
        assert callable(client.timing)
        return client

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            alog.debug(f"ASGI scope of type {scope['type']} is not supported yet")
            await self.app(scope, receive, send)
            return

        try:
            metric_name = self.metric_namer(scope)
        except AttributeError as e:
            alog.error(
                f"Unable to extract metric name from asgi scope: {scope}, skipping statsd timing"
            )
            alog.error(f" -> exception: {e}")
            await self.app(scope, receive, send)
            return

        def emit(stats):
            self.client.timing(f"{metric_name}", stats.time)

        with TimingStats(metric_name) as stats:
            try:
                await self.app(scope, receive, send)
            except Exception:
                stats.stop()
                emit(stats)
                raise
        emit(stats)
