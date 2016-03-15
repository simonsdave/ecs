# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

### Required

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

### Nice to Have

* improve feedback on bad request response
  * CID style + log aggregation / access
  * include errors in response

## Operations

### Required

* ecsctl.sh should spin up multiple ECS nodes
* ecsctl.sh should spin up ECS nodes across multiple GCE zones
* 401 from api domain should return json doc rather than HTML
* GCE forwarding rule should do health checks on nodes
* add instrumentation using [SignalFX](https://signalfx.com/)
* add log aggregation
* add status page using [Cachet](https://docs.cachethq.io/docs/get-started-with-docker)
  and [Pingdom](https://www.pingdom.com/)
  * [Pingdom API for check results](https://www.pingdom.com/resources/api#MethodGet+Raw+Check+Results)
  * [Cachet API for adding metrics](https://docs.cachethq.io/docs/get-metric-points)
* how should we describe the resources required by 1/ ecs service 2/ apidocs service
* document operational processes 
    * how to upgrade existing ECS cluster with new service code
    * how to increase and decrease size of ECS cluster

### Nice to Have

* automate godaddy DNS provisioning as per [this API spec](https://developer.godaddy.com/doc)
* where does Network Intrustion Detection and Host Intrustion Detection fit?

## Performance

### Required

* ...

### Nice to Have

* ```AsyncEndToEndContainerRunner``` should delete container using ```AsyncContainerDelete```
  after responding to the invoker of ```AsyncEndToEndContainerRunner``` - this should eliminate
  ~1 second overhead introduced by ```ecs```
* ```AsyncContainerLogs``` makes 2 requests to the Docker Remote API - to
  retrieve stdout and stderr - really should only need to do that once but
  can't seem to figure out this 8-byte header

## Stability

* (long running) load/stress test
* write some integration tests for private repos

## Documentation

* need some overview diagrams in the API docs
  * 2-tier - LB in-front of ECS cluster
  * request servicing pipeline
* add actual performance expectation numbers in API docs
* $KEY and $SECRET in API docs should be $ECS_KEY and $ECS_SECRET

## CI / CD

* why is Travis CI failing any and all Tornado Async unit tests
* why is Travis CI failing all integration tests
* build ecs docker images from .travis.yml
