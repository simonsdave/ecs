# Contributing

## Dev process

* To increase predicability, it is recommended
that ECS development be done on a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 14.04](http://releases.ubuntu.com/14.04/).
Instructions for spinning up such a VM can be found [here](../dev_env).
These instructions will also demonstrate how to ```git clone``` the
repo and run all the unit tests
* [Fork & Pull](https://help.github.com/articles/types-of-collaborative-development-models/#fork--pull)
is the preferred development model

## Testing

* ...

## CI

* [Travis](https://travis-ci.org/) is used to implement ECS' CI process
* see [.travis.yml](../.travis.yml) for details - summary of what's
done for each build:
  * dev environment configured from base Ubuntu 14.04 image
  * code checked out
  * static code analysis (pep8 & flake8)
  * unit, integration and load tests executed
* [Travis](https://travis-ci.org/) does not run a build as a result of a PR

## Docker Images

* docker images are built by the [Travis](https://travis-ci.org/) CI process
* leveraging [Travis' Default Environment Variables](https://docs.travis-ci.com/user/environment-variables/#Default-Environment-Variables)
the CI process ensures that
docker images are only built from the ```master``` and release (```v#.#.#```) branches
* ```Dockerfiles``` for building all ECS docker images are found [here](../dockerfiles)
* docker images are hosted on [DockerHub](https://hub.docker.com/search/?q=simonsdave%2Fecs)
* if docker images are built they are always pushed to [DockerHub](https://hub.docker.com/u/simonsdave/) automagically
* images tagged with ```latest``` represent the ```HEAD``` of the ```master``` branches

## Releasing a New Version of ECS

* releasing a new version of ECS starts and ends with creating a
new release in [github](https://github.com/simonsdave/ecs/releases)
* creating the new release starts a build in [Travis](https://travis-ci.org/)
and this build will create docker images tagged with the same tag
as the tag used to create the github release - done:-)
* released docker images are considered immutable once they are created
