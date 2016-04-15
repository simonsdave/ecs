# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

### Required

* /tasks needs to better handle scenerio where multiple clients are doing
  docker pulls @ the same time - load tests are currently failing because
  we're ignoring ```Repository .+ already being pulled by another client. Waiting.```
  ```_on_chunk()``` messages
* load tests need to run against real ECS deployment (handle HTTPS, authentication, etc)
* write some integration tests for private repos
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

* ecsctl.sh should support use of static IP for forwarding rule
* ecsctl.sh should spin up ECS nodes across multiple GCE zones
* add log aggregation
  * [Docker - configure logging drivers](https://docs.docker.com/engine/admin/logging/overview/)
  * [16 Apr '15 - SumoLogic - New Docker Logging Drivers](https://www.sumologic.com/2015/04/16/new-docker-logging-drivers/)
  * [10 Feb '16 - There is a “LOG”! Introducing Splunk Logging Driver in Docker 1.10.0](http://blogs.splunk.com/tag/splunk-logging-driver/)
  * [16 Dec '16 - Splunk Logging Driver for Docker](http://blogs.splunk.com/2015/12/16/splunk-logging-driver-for-docker/)
  * for Splunk Logging Driver need @ least version 1.10 of docker
  * [CoreOS release channels](https://coreos.com/releases/) which indicate Alpha channel is required
  * [How to get HTTP Event Collectors enabled in Splunk Cloud?](https://answers.splunk.com/answers/323085/how-to-get-http-event-collectors-enabled-in-splunk.html)
  * [HTTP Event Collector walkthrough](http://dev.splunk.com/view/event-collector/SP-CAAAE7F)
  * [30 Apr '15 - Integrating Splunk with Docker, CoreOS, and JournalD](http://blogs.splunk.com/2015/04/30/integrating-splunk-with-docker-coreos-and-journald/)
  * [14 Apr '16 - Sending Error Logs using Docker, Vagrant and SumoLogic](http://www.macadamian.com/2016/04/14/sending-error-logs-using-docker-vagrant-and-sumologic)
* add status page using [StatusPage.io](https://www.statuspage.io)
* how are we going to do SLA monitoring? can extract check results from [Pingdom](https://www.pingdom.com/) using the [Pingdom API for check results](https://www.pingdom.com/resources/api#MethodGet+Raw+Check+Results)

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

* in ```cloud-config.yaml``` how should we describe the resources required by ecs service and apidocs service
* add support to ```ecsctl.sh``` for increasing and decreasing size of ECS cluster
* how to upgrade existing ECS cluster with new service code
    * don't change IPs, DNS, forwarding rule, etc.
    * just want to replace nodes behind forward rule
    * think about using [docker tags](https://medium.com/@mccode/the-misunderstood-docker-tag-latest-af3babfd6375#.x4xg3qhgn)
      as an approach for identifying targets for upgrade

```bash
>sudo docker pull simonsdave/cloudfeaster:latest
>sudo docker images
REPOSITORY                    TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
simonsdave/cloudfeaster       latest              d3884baf3343        23 hours ago        769 MB
ubuntu                        14.04               ab035c88d533        2 weeks ago         187.9 MB
>sudo docker tag d3884baf3343 simonsdave/cloudfeaster:0.6.0
>sudo docker images
REPOSITORY                    TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
simonsdave/cloudfeaster       0.6.0               d3884baf3343        23 hours ago        769 MB
simonsdave/cloudfeaster       latest              d3884baf3343        23 hours ago        769 MB
ubuntu                        14.04               ab035c88d533        2 weeks ago         187.9 MB
>sudo docker login
>sudo docker push simonsdave/cloudfeaster
```

* [Core OS updates](https://coreos.com/using-coreos/updates/)
  * [CoreOS Update Strategy](https://coreos.com/os/docs/latest/update-strategies.html)
  * does nginx's # of active connections
    [ngx_http_stub_status_module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html)
    help with figuring out when it's ok to reboot?
* [CoreOS Hardening](https://coreos.com/os/docs/latest/coreos-hardening-guide.html)

### Nice to Have

* consider using [CoreOS Ignition](https://coreos.com/blog/introducing-ignition.html)
  when it gets to the beta channel
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

* setup and execute long running stress tests against an ECS deployment

## Documentation

* add 1/ forward rule to node health checks 2/ pingdom health checks
* add CoreOS updates to security section
* need some overview diagrams in the API docs
  * 2-tier - LB in-front of ECS cluster
  * request servicing pipeline
* add actual performance expectation numbers in API docs
* add CoreOS updates to security section
* add monitoring section
  * note can't SSH into a deployment so gotta have other ways to understand a
    deployment's operational behavior
  * health checks - 1/ forwarding rule to node 2/ pingdom
  * SignalFX - system metrics, custom metrics & "top" using [docker-collectd](https://github.com/signalfx/docker-collectd) and
    [docker-collectd-plugin](https://github.com/signalfx/docker-collectd-plugin)
  * StatusPage.io for quick visual check
  * incident management

## CI / CD

* ...
