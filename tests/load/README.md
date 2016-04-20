# Load

Tests and documentation to think through, determine and validate
service performance and stability under load/stress.

### What do I need to setup before running the tests?

```bash
>pip install --requirement requirements.txt
```

## Load Test A Real ECS Deployment

```run_load_test.sh``` can also be used to run a load tests against
a real ECS deployment. There are a couple of things about this kind
of deployment that need to be considered.

* need to get ```run_load_test.sh``` to load test the existing
deployment instead of spinning up a node

```bash
>ECS_ENDPOINT=https://api.ecs.cloudfeaster.com ./run_load_test.sh -v
Find locust log file @ '/tmp/tmp.aacQxEvsv1' for 10 concurrency
Find locust output @ '/tmp/tmp.fPFYvZEcCZ' for 10 concurrency
.
.
.
>
```

* a real ECS deployment requires authentication - the ```ecsctl.sh creds```
command generates a set of key/secret pairs

```bash
>ecsctl.sh creds
Putting hashed credentials in new file '/home/vagrant/ecs/bin/.htpasswd'
b35ec3fd96564323898920d282c18bb6:21023ce203851e7ec3eb1d25daf0fbcc
8d90c8aa5256454b974582c7f0c7fa76:5668c4e0d53901b26b2e4af6a7229f7d
731f1781575d430c9be46231fc7ad4c5:8e1a9ced90bd606bb5a1b3844b8f2299
1c78d19f3a2942a285c7091221808557:b4140392e719d0e7c6acd1e0e3bb1c12
cdf539dd1ba649e893950fa9f3de9f49:633ad1feaa40f2ecf1776b301e894340
>
```

Next we need to tell ```run_load_test.sh``` to use these credentials.
Assuming the output of ```ecsctl.sh creds``` is saved in ```~/.ecs/.htpasswd```,
the following will do the trick

```bash
>ECS_ENDPOINT=https://api.ecs.cloudfeaster.com ECS_CREDENTIALS=~/.ecs/.htpasswd ./run_load_test.sh -v
Find locust log file @ '/tmp/tmp.aacQxEvsv1' for 10 concurrency
Find locust output @ '/tmp/tmp.fPFYvZEcCZ' for 10 concurrency
.
.
.
>
```

* final thing ... load tests are intented to stress an ECS deployment
and generate traffic that looks a lot like a DoS attack.
the typical ECS deployment has per node rate limiting rules in place
ie. nodes have defenses in place to protect themselves again DoS
or general abuse. so, if you're going to load test a real ECS deployment
then you'll want to significantly increase the rates. at this time the
only way to increase the rates is to configure them when the deployment is
being spun up. the ```deployment.json``` below illustrates how to set
these rates. take a look @ the ECS API docs for the default rates.

```bash
>cat deployment.json
{
    "docs_domain": "docs.ecs.cloudfeaster.com",
    "api_domain": "api.ecs.cloudfeaster.com",
    "docs_cert": "/vagrant/docs.ecs.cloudfeaster.com.ssl.bundle.crt",
    "docs_key": "/vagrant/docs.ecs.cloudfeaster.com.key",
    "api_cert": "/vagrant/api.ecs.cloudfeaster.com.ssl.bundle.crt",
    "api_key": "/vagrant/api.ecs.cloudfeaster.com.key",
    "api_credentials": "/vagrant/.htpasswd",
    "dh_parameter": "/vagrant/dhparam.pem",
    "api_rate_limiting": {
        "per_ip": {
            "rate_limit": "5000r/s",
            "conn_limit": "5000"
        },
        "per_key": {
            "rate_limit": "500r/s",
            "conn_limit": "500"
        }
    },
    "number_of_nodes": 1
}
>
```

## NewRelic

[NewRelic](http://newrelic.com/) is a great
[APM](https://en.wikipedia.org/wiki/Application_performance_management)
service that can be very useful for performance tunning.
Running ECS under the NewRelic agent while ECS is servicing
requests from a load test generates lots of data for analysis.
ECS is written using [Tornado 4.3](http://www.tornadoweb.org/en/stable/)
and NewRelic's support for Toronado has been a bit spotty.
As of 30 Mar '16, [version 2.62.0.47 of NewRelic's python agent](https://docs.newrelic.com/docs/agents/python-agent/hosting-mechanisms/introductory-tornado-4-support)
claims to have support for Tornado 4.3 but running ECS under this
agent generates stack traces. Have asked NewRelic for help in finding
the root of the problem.

* [newrelic.ini](newrelic.ini) was generated per the instructions
  outlined [here](https://pypi.python.org/pypi/newrelic) (pip install
  new relic and then ```newrelic-admin generate-config %LICENSE_KEY% newrelic.ini```)
  and [here](https://docs.newrelic.com/docs/agents/python-agent/hosting-mechanisms/introductory-tornado-4-support) (add ```feature_flag = tornado.instrumentation.r3```
  to [newrelic.ini](newrelic.ini))
* you'll need to replace ```%LICENSE_KEY%``` in [newrelic.ini](newrelic.ini)
  with your own license key
* use the following to run ECS under the NewRelic agent
  ```NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program ecservice.py```
