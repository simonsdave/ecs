# Load

Tests and documentation to think through, determine and validate
service performance and stability under load/stress.

### What do I need to setup before running the tests?

```bash
>pip install --requirement requirements.txt
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
