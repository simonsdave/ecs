# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

* ephemeral_container_service.py -> ecs.py
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
* error detecting image not found; getting ```500 Internal Server Error``` rather than the expected```404 Not Found```
```bash
>cat echo.json
{
  "docker_image": "xubuntu",
  "tag": "latest",
  "cmd": [
    "date"
  ]
}
>curl -v -s -u $KEY:$SECRET -X POST -H "Content-Type: application/json" --data-binary @echo.json $ECS_ENDPOINT/v1.0/tasks
```

## Operations

* ecsctl.sh should spin up multiple ECS nodes
* ecsctl.sh should spin up ECS nodes across multiple GCE zones
* 401 from api domain should return json doc rather than HTML
* GCE forwarding rule should do health checks on nodes
* add instrumentation using [SignalFX](https://signalfx.com/)
* add status page using [Cachet](https://docs.cachethq.io/docs/get-started-with-docker)
and [Pingdom](https://www.pingdom.com/)
  * [Pingdom API for check results](https://www.pingdom.com/resources/api#MethodGet+Raw+Check+Results)
  * [Cachet API for adding metrics](https://docs.cachethq.io/docs/get-metric-points)
* how should we describe the resources required by 1/ ecs service 2/ apidocs service
* where does Network Intrustion Detection and Host Intrustion Detection fit?
* document operational processes 
    * how to upgrade existing ECS cluster with new service code
    * how to increase and decrease size of ECS cluster

## Performance

* ```AsyncEndToEndContainerRunner``` should delete container using ```AsyncContainerDelete```
  after responding to the invoker of ```AsyncEndToEndContainerRunner``` - this should eliminate
  ~1 second overhead introduced by ```ecs```

## Stability

* (long running) load/stress test
* write some integration tests for private repos

## Documentation

* add actual performance expectations numbers

## CI / CD

* why is Travis CI failing any and all Tornado Async unit tests
* why is Travis CI failing all integration tests
* build ecs docker images from .travis.yml
