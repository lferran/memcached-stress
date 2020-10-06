import asyncio
import random
import time

from guillotina import glogging
from guillotina.contrib import memcached

logger = glogging.getLogger("stress")


class MemcachedStress:
    def __init__(
        self,
        request_rate=20,
        duration=60,
        object_size_mean=7750,
        object_size_variance=2000,
        n_keys=10_000,
        get_prob=0.4,
        set_prob=0.3,
        delete_prob=0.2,
    ):
        self.request_rate = request_rate
        self.duration = duration  # minutes
        self.driver = None
        self._keys = self._setup_keys(n_keys)
        self.object_size_mean = object_size_mean
        self.object_size_variance = object_size_variance
        self.op_probs = {"get": get_prob, "set": set_prob, "delete": delete_prob}

    def _setup_keys(self, n_keys=10_000):
        """
        We want a deterministic set of keys!
        """
        return [f"stresstest-{i}" for i in range(n_keys)]

    def get_value_size(self):
        """Size of objects in cache follow a gaussian distribution.

        """
        return max(
            1, int(random.gauss(self.object_size_mean, self.object_size_variance))
        )

    def get_op(self):
        return random.choices(
            population=["get", "set", "delete"],
            weights=[
                self.op_probs["get"],
                self.op_probs["set"],
                self.op_probs["delete"],
            ],
        )[0]

    def get_key(self):
        """Choose one key at random with uniform distribution.

        """
        return random.choice(self._keys)

    def get_value(self):
        return ("D" * self.get_value_size()).encode()

    def iter_traffic_stages(self):
        """
        Performs stages of % of the full traffic
        """
        for duration_ratio, traffic_ratio in [
            (0.083, 0.25),
            (0.167, 0.5),
            (0.33, 0.75),
            (0.4167, 1),
        ]:
            yield duration_ratio, traffic_ratio

    async def random_memcached_op(self):
        """
        Executes a random memcached operation
        """
        # Sleep random amount of time to avoid having too much
        # contention when getting a free connection
        sleep_time = random.randint(0, 1000) / 1000
        await asyncio.sleep(sleep_time)

        op = self.get_op()
        key = self.get_key()
        args = []
        if op == "set":
            value = self.get_value()
            args.append(value)
        func = getattr(self.driver, op)
        await func(key, *args)

    async def execute_n_ops(self, n):
        ops = [self.random_memcached_op() for i in range(n)]
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
                    f"Starting phase {i} at {percent}% of traffic ({reqs_sec} reqs/sec) during {minutes:.1f} minutes"  # noqa
                )
                await asyncio.wait_for(
                    self.generate_traffic(traffic_ratio), timeout=minutes * 60
                )
            except asyncio.TimeoutError:
                logger.info(f"Finished phase {i}")

    async def run(self):
        logger.info(
            f"Starting experiment: up to {self.request_rate} ops/second rate for {self.duration} minutes"
        )
        await self.initialize()
        try:
            await self.run_traffic()
        except KeyboardInterrupt:
            logger.info("Halting experiment")
        await self.finalize()
        logger.info("Finished experiment")
