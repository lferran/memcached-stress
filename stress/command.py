import asyncio
import logging
from datetime import datetime

import prometheus_client
from aiohttp import web
from guillotina import glogging
from guillotina.commands import Command

from .memcached import MemcachedStress

logger = glogging.getLogger("stress")


async def prometheus_view(request):
    output = prometheus_client.exposition.generate_latest()
    return web.Response(text=output.decode("utf8"))


class StressTestCommand(Command):
    """
    Usage:
        g -c config.json stress --rate 50 --time 60

    """

    def get_parser(self):
        parser = super().get_parser()
        # add command arguments here...
        parser.add_argument(
            "-r", "--rate", help="Memcached op rate in ops/second", type=int, default=20
        )
        parser.add_argument(
            "-t",
            "--time",
            help="Total experiment time (in minutes)",
            type=int,
            default=60,
        )
        return parser

    def run(self, arguments, settings, app):
        if arguments.debug:
            logger._logger.setLevel(logging.DEBUG)

        memcached = MemcachedStress(request_rate=rate, duration=duration)
        loop = self.get_loop()
        asyncio.ensure_future(memcached.run(), loop=loop)

        app = web.Application()
        app.router.add_get("/metrics", prometheus_view)
        web.run_app(app, port=8080, host="0.0.0.0")
