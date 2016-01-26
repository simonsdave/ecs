# Ephemeral Container Service (ecs)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
![Python 2.7](https://img.shields.io/badge/python-2.7-FFC100.svg?style=flat)
[![Requirements Status](https://requires.io/github/simonsdave/ecs/requirements.svg?branch=master)](https://requires.io/github/simonsdave/ecs/requirements/?branch=master)
[![Build Status](https://travis-ci.org/simonsdave/ecs.svg?branch=master)](https://travis-ci.org/simonsdave/ecs)
[![Coverage Status](https://coveralls.io/repos/github/simonsdave/ecs/badge.svg?branch=master)](https://coveralls.io/github/simonsdave/ecs?branch=master)

```bash
> cat ~/.ecs/config
[ecs]
address=127.0.0.1
port=8448
log_level=info
max_concurrent_executing_http_requests=250
```

```bash
> curl -s http://127.0.0.1:8448/v1.0/ecs/_noop | jq
{
  "links": {
    "self": {
      "href": "http://127.0.0.1:8448/v1.0/ecs/_noop"
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
      "href": "http://127.0.0.1:8448/v1.0/ecs/_health"
    }
  }
}
```

```bash
> cat ecs.json
{
    "docker_image": "simonsdave/gaming-spiders",
    "tag": "latest",
    "cmd": [
        "sleep",
        "5"
    ]
}
> curl -s -X POST -v -H "Content-Type: application/json" --data-binary @ecs.json http://127.0.0.1:8448/v1.0/ecs | jq
```

```bash
> for x in $(sudo docker ps -a | awk '{print $1}'); do sudo docker rm $x >& /dev/null; done
```
