from guillotina import configure

app_settings = {
    "applications": ["guillotina.contrib.memcached"],
    "commands": {"stress": "stress.command.StressTestCommand"},
    "memcached": {
        "timeout": 120,
        "max_connections": 4,
        "purge_unused_connections_after": None,
        "purge_unhealthy_nodes": True,
    },
}


def includeme(root):
    configure.scan("stress.command")
