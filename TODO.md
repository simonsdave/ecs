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
* **branded** 404 response on invalid pages to docs domain

```bash
>curl https://docs.ecs.cloudfeaster.com/whatever
<html>
<head><title>404 Not Found</title></head>
<body bgcolor="white">
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

* [limit "size" of acceptable inbound payload](http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size)

## Operations

* use basic auth implemented in nginx
    * http://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
    * https://www.digitalocean.com/community/tutorials/how-to-set-up-http-authentication-with-nginx-on-ubuntu-12-10
* root CA on Ubuntu when using TLS/SSL certs from SSLs.com
* add rating limiting capability in API docs
* add instrumentation using ?DataDog? ?SignalFX?
* add status page using [Cachet](https://docs.cachethq.io/docs/get-started-with-docker)
and [Pingdom](https://www.pingdom.com/)
* add iptables rate limiting - why?
* put 'correct' TLS configuration in nginx
* how should we describe the resources required by 1/ ecs service 2/ apidocs service
* document operational processes 

## Performance

* ```AsyncEndToEndContainerRunner``` should delete container using ```AsyncContainerDelete```
  after responding to the invoker of ```AsyncEndToEndContainerRunner``` - this should eliminate
  ~1 second overhead introduced by ```ecs```

## Stability

* (long running) load/stress test
* write some integration tests for private repos

## API Documentation

* add actual performance expectations numbers

## CI / CD

* why is Travis CI failing any and all Tornado Async unit tests
* why is Travis CI failing all integration tests
* build ecs docker images from .travis.yml
