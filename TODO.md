# TODO

Fine grained list of to do's in order to make ```ecs``` production ready

## Functional

* need authentication for ```/_health``` endpoint
* sort out ```AsyncContainerLogs``` correctly fetching stdout & stderr
  using a single call to the Docker Remote API - think this mostly comes
  down to sorting out how to interpret the 8-byte header in the response
  from the Docker Remote API
* ```AsyncEndToEndContainerRunner``` needs to deal with failure scenarios
  more effectively - specifically it needs to delete containers on failure
  rather than just exiting
* ```curl --insecure -s -v -H 'Host: docs.ecs.cloudfeaster.com' https://127.0.0.1/random``` should generate ecs "branded" 404 page

## Operations

* create CoreOS ```cloud-config``` and provisioning scripts
* support client cert for authentication and authorization
* add instrumentation using ?DataDog?
* [nginx.site](https://github.com/simonsdave/ecs/blob/master/dockerfiles/nginx/nginx.site)
  contains references to ```cloudfeaster.com``` - what should happen 1/ rename nginx.site 
  to nginx.site.template and %DOMAIN% all cloudfeaster.com references 2/ change
  [nginx.sh](https://github.com/simonsdave/ecs/blob/master/dockerfiles/nginx/nginx.sh)
  to dynamically replace all %DOMAIN% references
* add iptables rate limiting - why?
* [nginx/nginx.site](nginx/nginx.site) has references to cloudfeaster - need to change this to support any organization
* put 'correct' TLS configuration in nginx
* require TLS client cert in [nginx/nginx.site](nginx/nginx.site)
* use [Let's Encrypt](https://letsencrypt.org/) to automate the generation of certs?
* use [Let's Encrypt](https://letsencrypt.org/) to automate the renewal of certs?
* how should we describe the resources required by 1/ ecs service 2/ apidocs service

## Performance

* ```AsyncEndToEndContainerRunner``` should delete container using ```AsyncContainerDelete```
  after responding to the invoker of ```AsyncEndToEndContainerRunner``` - this should eliminate
  ~1 second overhead introduced by ```ecs```

## Stability

* (long running) load/stress test
* write some integration tests for private repos

## API Documentation

* more samples
* add performance expectations

## CI

* why is Travis CI failing any and all Tornado Async unit tests
* why is Travis CI failing all integration tests
* build ecs docker images from .travis.yml
