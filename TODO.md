# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

### Required

* /tasks needs to better handle scenerio where multiple clients are doing
  docker pulls @ the same time - load tests are currently failing because
  we're ignoring ```Repository .+ already being pulled by another client. Waiting.```
  ```_on_chunk()``` messages

```bash
> curl -s -v 'http://172.17.42.1:2375/images/json?filter=ubuntu' | jq
* Hostname was NOT found in DNS cache
*   Trying 172.17.42.1...
* Connected to 172.17.42.1 (172.17.42.1) port 2375 (#0)
> GET /images/json?filter=ubuntu HTTP/1.1
> User-Agent: curl/7.35.0
> Host: 172.17.42.1:2375
> Accept: */*
>
< HTTP/1.1 200 OK
< Content-Type: application/json
< Date: Tue, 12 Apr 2016 12:49:56 GMT
< Content-Length: 265
<
{ [data not shown]
* Connection #0 to host 172.17.42.1 left intact
[
  {
    "Created": 1459964479,
    "Id": "41cc538fb83a158ab1f8f799142d3a37bed1ed6ea36ebf48c9b74aea7e97a741",
    "Labels": {},
    "ParentId": "2f2796dbe78d687c0d857e9344815f809cc72f46ed4f069835473c3844a14a54",
    "RepoDigests": [],
    "RepoTags": [
      "ubuntu:14.04"
    ],
    "Size": 0,
    "VirtualSize": 187934273
  }
]
> curl -X POST http://172.17.42.1:2375/images/create?fromImage=ubuntu:14.04
2016-04-12T12:20:27.645+00:00 INFO async_docker_remote_api _on_chunk() >>>{"status":"Repository ubuntu already being pulled by another client. Waiting."}<<<
```

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

* ```ecsctl.sh dep create``` should optionally permit specification of an ECS version number
  that will be used to identify docker images
* when ```ecsctl.sh``` starts a node, it should verify that the node has
  successfully started - perhaps the simplest thing to do is a curl
  to the /_health?quick=false endpoint
* add support to ```ecsctl.sh``` for increasing and decreasing size of ECS cluster
    * ```ecsctl.sh -v dep [rc|rmcap|remove_capacity]```
    * ```ecsctl.sh -v dep [ac|addcap|add_capacity]```
* how to upgrade / downgrade service code in an existing ECS cluster
    * don't change IPs, DNS, forwarding rule, etc.
        * in ```ecsctl.sh``` support use of static IP for forwarding rule
    * just want to replace nodes behind forward rule
    * use docker tags as an approach for identifying targets for upgrade
    * use can
* add log aggregation
  * [Docker - configure logging drivers](https://docs.docker.com/engine/admin/logging/overview/)
  * SumoLogic
      * [3 Apr '15 - Collecting and Analyzing CoreOS (journald) Logs w/ Sumo Logic](https://www.sumologic.com/2015/04/03/collecting-journald-logs-with-sumo-logic/)
      * [16 Apr '15 - SumoLogic - New Docker Logging Drivers](https://www.sumologic.com/2015/04/16/new-docker-logging-drivers/)
      * [14 Apr '16 - Sending Error Logs using Docker, Vagrant and SumoLogic](http://www.macadamian.com/2016/04/14/sending-error-logs-using-docker-vagrant-and-sumologic)
  * Splunk
      * [10 Feb '16 - There is a “LOG”! Introducing Splunk Logging Driver in Docker 1.10.0](http://blogs.splunk.com/tag/splunk-logging-driver/)
      * [16 Dec '16 - Splunk Logging Driver for Docker](http://blogs.splunk.com/2015/12/16/splunk-logging-driver-for-docker/)
      * for Splunk Logging Driver need @ least version 1.10 of docker
      * [CoreOS release channels](https://coreos.com/releases/) which indicate Alpha channel is required
      * [How to get HTTP Event Collectors enabled in Splunk Cloud?](https://answers.splunk.com/answers/323085/how-to-get-http-event-collectors-enabled-in-splunk.html)
      * [HTTP Event Collector walkthrough](http://dev.splunk.com/view/event-collector/SP-CAAAE7F)
      * [30 Apr '15 - Integrating Splunk with Docker, CoreOS, and JournalD](http://blogs.splunk.com/2015/04/30/integrating-splunk-with-docker-coreos-and-journald/)
* after implementing log aggregation, remove SSH access to nodes in an ECS cluster

* the SLA for an ECS deployment is expressed as:

> NN% of the time the ECS deployment will be available to process tasks
> (ie. POSTs to the /tasks endpoint will work) and the ECS infrastructure
> will add no more than X ms of overhead to a task

Every (1|5) minute(s) [Pingdom](https://www.pingdom.com/) issues two requests
into the ECS deployment.

1. a POST to the /tasks endpoint that runs a bash shell which immediately exits (:TODO: something in here about the time and availability of the docker registry on which the deployment depends - might need to seed each node with a docker image) - the POST is considered successful with a 201 Created response
1. a GET to the /_noop endpoint - the GET is considered successful with a 200 OK response

The overhead added by the ECS deployment is calculated by subtracting the response
time for (2) from the response time for (1).
At any point in time, the ECS deployment is considered available if both
(1) and (2) are successful **and** the overhead added by the ECS deployment
is less than some predefined threshold.

For some initial thoughts on implementation see [sla.py](bin/sla.py).


* [Core OS updates](https://coreos.com/using-coreos/updates/)
  * [CoreOS Update Strategy](https://coreos.com/os/docs/latest/update-strategies.html)
  * does nginx's # of active connections
    [ngx_http_stub_status_module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html)
    help with figuring out when it's ok to reboot?
* [CoreOS Hardening](https://coreos.com/os/docs/latest/coreos-hardening-guide.html)

### Nice to Have

* describe the resources required by ecs and apidocs service in ```cloud-config.yaml``` 
* add support for [CloudFlare](https://www.cloudflare.com)
* add status page using [StatusPage.io](https://www.statuspage.io)
* consider using [CoreOS Ignition](https://coreos.com/blog/introducing-ignition.html)
  when it gets to the beta channel
* 401 from api domain should return json content type
* ecsctl.sh should spin up ECS nodes across multiple GCE zones
* remove nginx version # from all responses
* ecsctl.sh (& other supporting files) aren't packaged in any distribution
  which means to use ecsctl.sh you need to git clone the ecs repo which isn't ideal.
  sort out how ecsctl.sh will be packaged.
* automate DNS provisioning
  * [GoDaddy](https://developer.godaddy.com/doc)
* where does Network Intrustion Detection and Host Intrustion Detection fit?

## Performance

### Required

* ...

### Nice to Have

* [load tests](tests/load) might benefit from incorporating the following
techniques into graphs so trends can be more easily identified vs the
bucketing approach currently being used
    * [exponential smoothing](https://en.wikipedia.org/wiki/Exponential_smoothing)
    * [autocorrelation (from 'pearson spectrum correlation')](https://en.wikipedia.org/wiki/Autocorrelation)
* ```AsyncEndToEndContainerRunner``` should delete container using ```AsyncContainerDelete```
  after responding to the invoker of ```AsyncEndToEndContainerRunner``` - this should eliminate
  ~1 second overhead introduced by ```ecs```
* ```AsyncContainerLogs``` makes 2 requests to the Docker Remote API - to
  retrieve stdout and stderr - really should only need to do that once but
  can't seem to figure out this 8-byte header
* once NewRelic really supports Tornado
    * optionally run agent when running load test
    * optionally make agent part of deployment

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
  * [New Relic Server](http://newrelic.com/server-monitoring) for monitoring
    docker host system metrics and [Docker Monitoring with New Relic](http://newrelic.com/docker) for docker container metrics
  * StatusPage.io for quick visual check
  * incident management

## CI / CD

* ```docker push``` in ```build-docker-image.sh``` occasionally fails; put
a retry loop on the ```docker push``` (& probably the ```docker login```)
to increase the probability of success
