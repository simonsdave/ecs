# Load

This directory contains tests and documentation to think through, determine
and validate service performance and stability under various load/stress scenarios.

[Locust](http://locust.io) is the core load testing tool used to drive
requests thru an ECS deployment. [run_load_test.sh](run_load_test.sh) is
a wrapper around [Locust](http://locust.io) which is responsible for
parsing the load test's json configuration file, optionally spinning up
a local [ecservice.py](../../bin/ecservice.py) and launching
[analyze_load_test_tsv.py](analyze_load_test_tsv.py) to analyze the
results of the load test.
[load-test-config-for-travis.json](load-test-config-for-travis.json)
is an example load test configuration file.

```bash
>jq . load-test-config-for-travis.json
{
  "number_of_requests": 1000,
  "hatch_rate": 5,
  "concurrency": [
    10,
    15,
    20,
    25
  ]
}
>
```

[Locust](http://locust.io) (along with
a few other packages) aren't loaded by default when configuring the dev
environment using ```source cfg4dev```. Before running load tests you
need to pip install all the required packages.

```bash
>pip install --requirement requirements.txt
.
.
.
```

Here's an example of running a basic load test
using [load-test-config-for-travis.json](load-test-config-for-travis.json).

```bash
>./run_load_test.sh -v load-test-config-for-travis.json
Started ECS - PID = 25792; config file '/tmp/tmp.Uydf4idUBC'
Find locust log file @ '/tmp/tmp.MvwVWYRJWi' for 10 concurrency
Find locust output @ '/tmp/tmp.XvNoa22lSK' for 10 concurrency
=======================================================================
1020 @ 12 from 2016-04-23 15:22:40.382000 to 2016-04-23 15:25:25.313000
=======================================================================

Request Type                 Ok Error            Min        50        60        70        80        90        95        99       Max
------------------------------------------------------------------------------------------------------------------------------------
Health-Check-Quick          212     0  21%         3         6         7         8        11        17        23        39        59
Health-Check-Slow           205     0  20%         6        16        19        24        30        47        64       134       269
NoOp                        207     0  20%         3         5         5         6         9        12        20        35        54
Tasks-Bad-Request-Body       19     0   2%         3        10        11        14        15        18        20        30        32
Tasks-Happy-Path            156     0  15%      3609      6598      6947      7683      8194      9507     11508     13133     16208
Tasks-Image-Not-Found        16     0   2%       171      1037      1255      1287      1624      2329      3139      4669      5052
Version                     205     0  20%         3         5         5         7        10        15        21        38        62

=======================================================================
Find locust log file @ '/tmp/tmp.oz8jtT8DbO' for 15 concurrency
Find locust output @ '/tmp/tmp.9AmoGUSVsq' for 15 concurrency
=======================================================================
1029 @ 16 from 2016-04-23 15:25:25.832000 to 2016-04-23 15:27:47.742000
=======================================================================

Request Type                 Ok Error            Min        50        60        70        80        90        95        99       Max
------------------------------------------------------------------------------------------------------------------------------------
Health-Check-Quick          342     0  33%         3         5         7         9        13        18        24        34        52
Health-Check-Slow           172     0  17%         6        17        20        22        29        71       129       383       477
NoOp                        177     0  17%         3         5         5         6         9        14        19        27        35
Tasks-Bad-Request-Body       16     0   2%         3         8        10        13        15        21        24        28        29
Tasks-Happy-Path            137     0  13%      1873      9488     10027     10604     11466     12571     14690     16663     18271
Tasks-Image-Not-Found        11     0   1%       400      1788      2255      3387      6228      9205     10546     11619     11888
Version                     174     0  17%         3         5         5         7        10        15        22        29        43

=======================================================================
Find locust log file @ '/tmp/tmp.OxasvQ1MLH' for 20 concurrency
Find locust output @ '/tmp/tmp.jncpZ5wF4F' for 20 concurrency
=======================================================================
1037 @ 20 from 2016-04-23 15:27:48.436000 to 2016-04-23 15:30:12.828000
=======================================================================

Request Type                 Ok Error            Min        50        60        70        80        90        95        99       Max
------------------------------------------------------------------------------------------------------------------------------------
Health-Check-Quick          347     0  33%         3         6         8        11        14        18        25        44        71
Health-Check-Slow           169     0  16%         6        16        19        22        31        52        79       187       369
NoOp                        171     0  16%         3         5         5         7        10        14        20        55       125
Tasks-Bad-Request-Body       12     0   1%         3         5         5         6         6         7        10        14        15
Tasks-Happy-Path            140     0  14%      4671     12972     13854     14365     16099     17641     18715     23087     26537
Tasks-Image-Not-Found        24     0   2%        73      1361      1555      1720      2143      2616      2742      3007      3083
Version                     174     0  17%         3         5         7         9        13        21        25        72        93

=======================================================================
Find locust log file @ '/tmp/tmp.jHvrWzDDnj' for 25 concurrency
Find locust output @ '/tmp/tmp.RX7wU6ninx' for 25 concurrency
=======================================================================
1048 @ 25 from 2016-04-23 15:30:13.320000 to 2016-04-23 15:32:22.134000
=======================================================================

Request Type                 Ok Error            Min        50        60        70        80        90        95        99       Max
------------------------------------------------------------------------------------------------------------------------------------
Health-Check-Quick          445     0  42%         3         5         6         8        12        18        25        39       112
Health-Check-Slow           144     0  14%         6        18        21        31        51        96       198       350       474
NoOp                        145     0  14%         3         5         7         9        12        18        23        47        79
Tasks-Bad-Request-Body       13     0   1%         3         5         5         5         6        16        26        36        38
Tasks-Happy-Path            133     0  13%      3155     15610     16779     17663     18891     20481     22416     26121     29900
Tasks-Image-Not-Found        17     0   2%       173      2048      2102      2422      2671      3710      4806      7564      8254
Version                     151     0  14%         3         5         6         8        10        15        17        33        71

=======================================================================
>
```

By default ```run_load_test.sh``` spins up a local ECS deployment.
```run_load_test.sh``` can also be used to run a load tests against
an existing ECS deployment with the inclusion of the ```endpoint``` property
in the load test configuration document.
If the ECS deployment requires authentication the load test configuration
document should include the ```credentials``` property which points to a file
containing the output of ```ecsctl.sh creds```.

```bash
>cat ecsctl-sh-creds-output.txt
b35ec3fd96564323898920d282c18bb6:21023ce203851e7ec3eb1d25daf0fbcc
8d90c8aa5256454b974582c7f0c7fa76:5668c4e0d53901b26b2e4af6a7229f7d
731f1781575d430c9be46231fc7ad4c5:8e1a9ced90bd606bb5a1b3844b8f2299
1c78d19f3a2942a285c7091221808557:b4140392e719d0e7c6acd1e0e3bb1c12
cdf539dd1ba649e893950fa9f3de9f49:633ad1feaa40f2ecf1776b301e894340
>
```

```bash
>cat deployment.json
{
    "number_of_requests": 100,
    "hatch_rate": 5,
    "concurrency": [5],
    "endpoint": "https://api.ecs.cloudfeaster.com",
    "credentials": "ecsctl-sh-creds-output.txt"
}
```

```bash
>./run_load_test.sh -v deployment.json
Find locust log file @ '/tmp/tmp.aacQxEvsv1' for 10 concurrency
Find locust output @ '/tmp/tmp.fPFYvZEcCZ' for 10 concurrency
.
.
.
>
```

Final thing ... load tests are intented to stress an ECS deployment
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

[New Relic](http://newrelic.com/) is a great
[APM](https://en.wikipedia.org/wiki/Application_performance_management)
service that can be very useful for performance tunning.
Running ECS under the New Relic agent while ECS is servicing
requests from a load test generates lots of data for analysis.
ECS is written using [Tornado 4.3](http://www.tornadoweb.org/en/stable/)
and New Relic's support for Tornado has been spotty.
As of 30 Mar '16, [version 2.62.0.47 of New Relic's python agent](https://docs.newrelic.com/docs/agents/python-agent/hosting-mechanisms/introductory-tornado-4-support)
claims to have support for Tornado 4.3 but running ECS under this
agent generates stack traces - see [this](https://support.newrelic.com/tickets/190024) for details.
The New Relic support team have been awesome and are sorting out the problem.

* [newrelic.ini](newrelic.ini) was generated per the instructions
  outlined [here](https://pypi.python.org/pypi/newrelic) (pip install
  new relic and then ```newrelic-admin generate-config %LICENSE_KEY% newrelic.ini```)
  and [here](https://docs.newrelic.com/docs/agents/python-agent/hosting-mechanisms/introductory-tornado-4-support) (add ```feature_flag = tornado.instrumentation.r3```
  to [newrelic.ini](newrelic.ini))
* you'll need to replace ```%LICENSE_KEY%``` in [newrelic.ini](newrelic.ini)
  with your own license key
* use the following to run ECS under the New Relic agent
  ```NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program ecservice.py```
