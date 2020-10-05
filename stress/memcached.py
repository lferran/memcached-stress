from guillotina.contrib import memcached
import random
import asyncio
import time
import logging
import string

logger = logging.getLogger("stress")


class MemcachedStress:
    def __init__(self, request_rate):
        self.request_rate = request_rate
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

    def random_key(self, key_length=50):
        key = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=key_length)
        )
        return f"stresstest-{key}"

    def get_key(self):
        return random.choice(self._keys)

    def get_value(self):
        return ("D" * self.get_value_size()).encode()

    def iter_traffic_stages(self):
        for minutes, traffic_ratio in [(5, 0.25), (10, 0.5), (20, 0.75), (25, 1)]:
            yield minutes, traffic_ratio

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
            print(f"Executing {n_requests} requests...")
            start = time.time()
            await self.execute_n_ops(n=n_requests)
            duration = time.time() - start
            await asyncio.sleep(1 - duration)

    async def initialize(self):
        # Initialize driver
        self.driver = await memcached.get_driver()

    async def finalize(self):
        await self.driver.finalize()

    async def run_traffic(self):
        for i, (minutes, traffic_ratio) in enumerate(self.iter_traffic_stages()):
            percent = int(traffic_ratio * 100)
            try:
                print(
                    f"Starting phase {i} at {percent}% of traffic during {minutes} minutes"
                )
                await asyncio.wait_for(
                    self.generate_traffic(traffic_ratio), timeout=minutes * 60
                )
            except asyncio.TimeoutError:
                print(f"Finished phase {i}")

    async def run(self):
        await self.initialize()
        await self.run_traffic()
        await self.finalize()
