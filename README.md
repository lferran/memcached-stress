# memcached-stress

Guillotina memcached driver stress-test k8s job.

  - Defines a k8s job that when deployed, will run a custom guillotina command.
  - Command generates traffic against a configured set of memcached instances.

The test runs for 1 hour, where traffic is gradually increased (25,
50, 70 and 100%, correspondingly after a few minutes each).

## Configuration

To configure memcached hosts
``` shell
export MEMCACHED_HOSTS="host1:11211, host2:11211"
```

To configure the amount of traffic
