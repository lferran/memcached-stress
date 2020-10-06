import asyncio
import random
import string
import time

from guillotina import glogging
from guillotina.contrib import memcached

logger = glogging.getLogger("stress")


class MemcachedStress:
    def __init__(self, request_rate=20, duration=60):
        self.request_rate = request_rate
        self.duration = duration  # minutes
        self.driver = None
        self._keys = self._setup_keys()

    def _setup_keys(self):
        """
        We want a deterministic set of keys!
        """
        return [f"stresstest-{i}" for i in range(10_000)]

    def get_value_size(self):
        """
        in bytes
        """
        return max(1, int(random.gauss(7750, 2000)))

    def get_op(self):
        op_probs = {"get": 0.5, "set": 0.3, "delete": 0.2}
        return random.choices(
            population=["get", "set", "delete"],
            weights=[op_probs["get"], op_probs["set"], op_probs["delete"]],
        )[0]

    def get_key(self):
        return random.choice(self._keys)

    def get_value(self):
        return ("D" * self.get_value_size()).encode()

    def iter_traffic_stages(self):
        for duration_ratio, traffic_ratio in [
            (0.083, 0.25),
            (0.167, 0.5),
            (0.33, 0.75),
            (0.4167, 1),
        ]:
            yield duration_ratio, traffic_ratio

    async def memcached_op(self):
        op = self.get_op()
        key = self.get_key()
        args = []
        if op == "set":
            value = self.get_value()
            args.append(value)
        func = getattr(self.driver, op)
        await func(key, *args)

    async def execute_n_ops(self, n):
        ops = [self.memcached_op() for i in range(n)]
        await asyncio.gather(*ops)

    async def generate_traffic(self, ratio=1):
        while True:
            n_requests = int(self.request_rate * ratio)
            logger.debug(f"Executing {n_requests} requests...")
            start = time.time()
            await self.execute_n_ops(n=n_requests)
            duration = time.time() - start
            await asyncio.sleep(max(0, 1 - duration))

    async def initialize(self):
        # Initialize driver
        self.driver = await memcached.get_driver()

    async def finalize(self):
        await self.driver.finalize()

    async def run_traffic(self):
        for i, (duration_ratio, traffic_ratio) in enumerate(self.iter_traffic_stages()):
            minutes = duration_ratio * self.duration
            percent = int(traffic_ratio * 100)
            reqs_sec = self.request_rate * traffic_ratio
            try:
                logger.info(
                    f"Starting phase {i} at {percent}% of traffic ({reqs_sec} reqs/sec) during {minutes:.1f} minutes"
                )
                await asyncio.wait_for(
                    self.generate_traffic(traffic_ratio), timeout=minutes * 60
                )
            except asyncio.TimeoutError:
                logger.info(f"Finished phase {i}")

    async def run(self):
        await self.initialize()
        try:
            await self.run_traffic()
        except KeyboardInterrupt:
            logger.info("Halting experiment")
        await self.finalize()
