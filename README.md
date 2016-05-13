# Ephemeral Container Service (ECS)
![Maintained](https://img.shields.io/maintenance/yes/2016.svg)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
![Python 2.7](https://img.shields.io/badge/python-2.7-FFC100.svg?style=flat)
[![Requirements Status](https://requires.io/github/simonsdave/ecs/requirements.svg?branch=master)](https://requires.io/github/simonsdave/ecs/requirements/?branch=master)
[![Build Status](https://travis-ci.org/simonsdave/ecs.svg?branch=master)](https://travis-ci.org/simonsdave/ecs)
[![Coverage Status](https://coveralls.io/repos/github/simonsdave/ecs/badge.svg?branch=master)](https://coveralls.io/github/simonsdave/ecs?branch=master)

The Ephemeral Container Service (ECS) was born out of
the [Cloudfeaster](https://github.com/simonsdave/cloudfeaster.git) project.
[Docker](https://www.docker.com/) makes it easy to package
short lived (aka ephemral) tasks in a docker image and run
those tasks using the docker client.
The [Docker Remote API](https://docs.docker.com/engine/reference/api/docker_remote_api/)
makes it possible to do this using requests to a RESTful API.
[Cloudfeaster](https://github.com/simonsdave/cloudfeaster.git) used
these building blocks to package [spiders](https://en.wikipedia.org/wiki/Web_crawler)
in docker images and run those spiders in docker containers on a cluster of docker hosts.
ECS is a generalization of these basic building blocks.

# What Next?

* [spin up a development environment](dev_env)
* [provision a cluster](docs/provisioning.md)
