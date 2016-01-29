# API (by example)

```bash
> curl -s http://127.0.0.1:8448/v1.0/ecs/_noop | jq
{
  "links": {
    "self": {
      "href": "http://127.0.0.1:8448/v1.0/_noop"
    }
  }
}
```

```bash
> curl -s http://127.0.0.1:8448/v1.0/ecs/_health | jq
{
  "status": "green",
  "links": {
    "self": {
      "href": "http://127.0.0.1:8448/v1.0/_health"
    }
  }
}
```

```bash
> cat ecs.json
{
    "docker_image": "ubuntu",
    "tag": "latest",
    "cmd": [
        "sleep",
        "5"
    ]
}
> curl -s -X POST -v -H "Content-Type: application/json" --data-binary @ecs.json http://127.0.0.1:8448/v1.0/tasks | jq
```

```bash
> cat crawl.json
{
    "docker_image": "someone/private-repo",
    "tag": "latest",
    "cmd": [
        "somecommand.sh",
        "arg1",
        "arg2"
    ],
    "creds": {
        "username": "something",
        "email": "something@example.com",
        "password": "password"
    }
} 
> curl -s -X POST -v -H "Content-Type: application/json" --data-binary @crawl.json http://127.0.0.1:8448/v1.0/tasks | jq
```
