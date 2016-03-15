This folder contains everything that's required to build
ECS' docker images and push those images
to [DockerHub](https://hub.docker.com). docker images published
to DockerHub are required before provisioning an ECS cluster.

ECS has 3 docker images:

* [ecs-apidocs](apidocs)
* [ecs-services](services)
* [ecs-nginx](nginx)

# Building Images

Instructions for building all ECS containers are below. First
```git clone``` the ECS repo.

```bash
>cd
>git clone git clone https://github.com/simonsdave/ecs.git
```

Configure the development environment.

```bash
>cd ecs
>source cfg4dev
```

Build the API docs.

```bash
>cd api_docs
>./build-api-docs.sh -t
>ls -l api_docs.tar
-rw-rw-r-- 1 vagrant vagrant 133120 Mar 14 19:50 api_docs.tar
>
```

Build services package.

```bash
>cd ..
>python setup.py sdist --formats=gztar
>
```

Build local copies of all docker images.

```bash
>cd dockerfiles
>build-docker-images.sh \
  -v \
  ../dist/ecs-0.8.0.tar.gz \
  ../api_docs/api_docs.tar \
  simonsdave
>
```
