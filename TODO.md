# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

### Required

* remove tag property from /tasks request body and instead support
  standard owner/repo:tag format
* ```AsyncEndToEndContainerRunner``` needs to deal with failure scenarios
  more effectively - specifically it needs to delete containers on failure
  rather than just returning

### Nice to Have

* improve feedback on bad request response
  * CID style + log aggregation / access
  * include errors in response
* support [docker registries](https://docs.docker.com/registry/) in
  addition to [DockerHub](https://hub.docker.com)

## Operations

### Required

* ecsctl.sh should spin up ECS nodes across multiple GCE zones
* add instrumentation using [SignalFX](https://signalfx.com/)
* add log aggregation
  * [Docker - configure logging drivers](https://docs.docker.com/engine/admin/logging/overview/)
  * [16 Apr '15 - SumoLogic - New Docker Logging Drivers](https://www.sumologic.com/2015/04/16/new-docker-logging-drivers/)
  * [10 Feb '16 - There is a “LOG”! Introducing Splunk Logging Driver in Docker 1.10.0](http://blogs.splunk.com/tag/splunk-logging-driver/)
  * [16 Dec '16 - Splunk Logging Driver for Docker](http://blogs.splunk.com/2015/12/16/splunk-logging-driver-for-docker/)
  * for Splunk Logging Driver need @ least version 1.10 of docker
  * [CoreOS release channels](https://coreos.com/releases/) which indicate Alpha channel is required
* add status page using [Cachet](https://docs.cachethq.io/docs/get-started-with-docker)
  and [Pingdom](https://www.pingdom.com/)
  * [Amazon RDS](http://aws.amazon.com/rds/)
  * [Pingdom API for check results](https://www.pingdom.com/resources/api#MethodGet+Raw+Check+Results)
  ```bash
    >PINGDOM_USERNAME=...
    >PINGDOM_PASSWORD=...
    >PINGDOM_APPKEY=...
    >curl -s -u "$PINGDOM_USERNAME:$PINGDOM_PASSWORD" -H "App-Key:$PINGDOM_APPKEY" "https://api.pingdom.com/api/2.0/checks" | jq
    >PINGDOM_CHECK_ID=...
    >curl -s -u "$PINGDOM_USERNAME:$PINGDOM_PASSWORD" -H "App-Key:$PINGDOM_APPKEY" "https://api.pingdom.com/api/2.0/results/$PINGDOM_CHECK_ID?limit=1440" | jq . > formatted_last_day_of_check_results.json
    >head -20 formatted_last_day_of_check_results.json
    {
      "activeprobes": [
        65,
        34,
        68,
        72,
        43,
        82,
        60
      ],
      "results": [
        {
          "probeid": 68,
          "time": 1458570747,
          "status": "down",
          "statusdesc": "Timeout (> 30s)",
          "statusdesclong": "Socket timeout, unable to connect to server"
        },
        {
          "probeid": 72,
    >tail -20 formatted_last_day_of_check_results.json
          "statusdesclong": "OK"
        },
        {
          "probeid": 82,
          "time": 1458510867,
          "status": "up",
          "responsetime": 508,
          "statusdesc": "OK",
          "statusdesclong": "OK"
        },
        {
          "probeid": 34,
          "time": 1458510807,
          "status": "up",
          "responsetime": 132,
          "statusdesc": "OK",
          "statusdesclong": "OK"
        }
      ]
    }
    ```
  * [Cachet API for adding metrics](https://docs.cachethq.io/docs/get-metric-points)
* how should we describe the resources required by 1/ ecs service 2/ apidocs service
* document operational processes 
  * how to upgrade existing ECS cluster with new service code
  * how to increase and decrease size of ECS cluster
* [CoreOS Update Strategy](https://coreos.com/os/docs/latest/update-strategies.html)
* [CoreOS Hardening](https://coreos.com/os/docs/latest/coreos-hardening-guide.html)

### Nice to Have

* 401 from api domain should return json content type
* remove nginx version # from all responses
* remove SSH access to nodes in ECS cluster
* automate GoDaddy DNS provisioning as per [this API spec](https://developer.godaddy.com/doc)
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

## CI / CD

* build ecs docker images from .travis.yml
