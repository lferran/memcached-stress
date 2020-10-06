import asyncio
import logging
from datetime import datetime

from guillotina import glogging
from guillotina.commands import Command

from .memcached import MemcachedStress

logger = glogging.getLogger("stress")


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
        rate = arguments.rate
        duration = arguments.time
        logger.info(
            f"Starting experiment: up to {rate} ops/second rate for {duration} minutes"
        )
        if arguments.debug:
            logger._logger.setLevel(logging.DEBUG)

        memcached = MemcachedStress(request_rate=rate, duration=duration)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(memcached.run())
        logger.info(f"Finished experiment")
