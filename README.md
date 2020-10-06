# memcached-stress

Guillotina memcached driver stress-test k8s job.

  - Defines a k8s job that when deployed, will run a custom guillotina command.
  - Command generates traffic against a configured set of memcached instances.

The test runs for 1 hour, where traffic is gradually increased (25,
50, 70 and 100%, correspondingly after a few minutes each).

## Docker

Start a memcached instance
``` shell
docker run -p 11211:11211 -d memcached:1.6.7
```

Build the image

``` shell
docker build --network host --no-cache -t memcached-test:local .
```

Run the stress test

``` shell
docker run --env MEMCACHED_HOSTS="localhost:11211" memcached-test:local g -c config.json stress --time 60 --rate 20
```

## Configuration

Set the following environment variable to configure memcached hosts
``` shell
export MEMCACHED_HOSTS="host1:11211, host2:11211"
```

To configure the amount of traffic


## Run the command

This will run the experiment up to 20 requests per second for 60
minutes

``` shell
g -c config.json stress --rate=20 --time=60
```
