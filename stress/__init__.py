from os import environ

from guillotina import configure


def get_hosts():
    try:
        HOSTS = environ["MEMCACHED_HOSTS"]
        if "," in HOSTS:
            hosts = [h.strip() for h in HOSTS.split(",")]
        else:
            hosts = HOSTS
        return hosts
    except KeyError:
        raise Exception(
            'MEMCACHED_HOSTS env variable missing e.g: export MEMCACHED_HOSTS="host-1:11211, host-2:11211"'
        )


app_settings = {
    "applications": ["guillotina.contrib.memcached"],
    "commands": {"stress": "stress.command.StressTestCommand"},
    "memcached": {
        "hosts": get_hosts(),
        "timeout": 120,
        "max_connections": 4,
        "purge_unused_connections_after": None,
        "purge_unhealthy_nodes": True,
    },
}


def includeme(root):
    configure.scan("stress.command")
