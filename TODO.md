# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

* improve feedback on bad request response
  * CID style + log aggregation / access
  * include errors in response
* sort out ```AsyncContainerLogs``` correctly fetching stdout & stderr
  using a single call to the Docker Remote API - think this mostly comes
  down to sorting out how to interpret the 8-byte header in the response
  from the Docker Remote API
* ```AsyncEndToEndContainerRunner``` needs to deal with failure scenarios
  more effectively - specifically it needs to delete containers on failure
  rather than just exiting
* [limit "size" of acceptable inbound payload](http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)
* error detecting image not found
    * ```curl -v -X POST "http://172.17.42.1:2375/images/create?fromImage=xubuntu&tag=latest"```
```json
{
  "docker_image": "xubuntu",
  "tag": "latest",
  "cmd": [
    "date"
  ]
}
```
    * ```curl -v -s -u $KEY:$SECRET -X POST -H "Content-Type: application/json" --data-binary @echo.json $ECS_ENDPOINT/v1.0/tasks``` will result in ```500 Internal Server Error``` rather than ```404 Not Found```

## Operations

* put 'correct' TLS configuration in nginx
* deploy across multiple GCE zones
* [enable iptables](https://www.jimmycuadra.com/posts/securing-coreos-with-iptables/)
* 401 from api domain should return json doc rather than HTML
* GCE forwarding rule should do health checks on nodes
* add instrumentation using ?DataDog? ?SignalFX?
* root CA on Ubuntu when using TLS/SSL certs from SSLs.com
* add status page using [Cachet](https://docs.cachethq.io/docs/get-started-with-docker)
and [Pingdom](https://www.pingdom.com/)
* how should we describe the resources required by 1/ ecs service 2/ apidocs service
* document operational processes 

## Performance

* ```AsyncEndToEndContainerRunner``` should delete container using ```AsyncContainerDelete```
  after responding to the invoker of ```AsyncEndToEndContainerRunner``` - this should eliminate
  ~1 second overhead introduced by ```ecs```

## Documenation

* add rating limiting capability in API docs

## Stability

* (long running) load/stress test
* write some integration tests for private repos

## API Documentation

* add actual performance expectations numbers

## CI / CD

* why is Travis CI failing any and all Tornado Async unit tests
* why is Travis CI failing all integration tests
* build ecs docker images from .travis.yml
