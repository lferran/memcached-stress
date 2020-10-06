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
        g -c config.json --rate 50

    """

    def get_parser(self):
        parser = super().get_parser()
        # add command arguments here...
        parser.add_argument(
            "-r", "--rate", help="Memcached op rate in ops/second", type=int, default=20
        )
        return parser

    def run(self, arguments, settings, app):

        rate = arguments.rate
        start = datetime.utcnow()

        logger.info(f"Starting at {start} with a {rate} ops/second rate")

        if arguments.debug:
            logger._logger.setLevel(logging.DEBUG)

        memcached = MemcachedStress(rate)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(memcached.run())

        end = datetime.utcnow()
        logger.info(f"Finished at {end}")
