from guillotina.commands import Command
from .memcached import MemcachedStress
import asyncio
from datetime import datetime


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
        print(f"Starting at {start} with a {rate} ops/second rate")

        memcached = MemcachedStress(rate)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(memcached.run())

        end = datetime.utcnow()
        print(f"Finished at {end}")
