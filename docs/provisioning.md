# Provisioning

These instructions describe how to ...

## Setup Google Compute Engine Project

* setup a project in the
[Google Developer Console](https://console.developers.google.com/project) - in
the instructions below the project will be called ```ecs```

* enable the ```compute engine API``` in
the [Google Developer Console](https://console.developers.google.com/project)

* ```gcloud auth login```

* ```gcloud config set project ecs```

* ```gcloud config set compute/zone us-central1-a```

## Create SSL/TLS certs

* create api and docs SSL/TLS certs

## Choose Domain Names

* for api and docs

## Spin up a deployment

* ...

```bash
> ./ecsctl.sh -v dep create docs.ecs.cloudfeaster.com api.ecs.cloudfeaster.com /vagrant/docs.ecs.cloudfeaster.com.crt /vagrant/docs.ecs.cloudfeaster.com.key /vagrant/api.ecs.cloudfeaster.com.crt /vagrant/api.ecs.cloudfeaster.com.key
>
```

## Configure DNS

* ...

## Exploring Endpoints

```bash
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1 | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/random | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0 | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_health | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_health?quick=false | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_noop | jq
```

## Exploring Rate Limiting
```bash
> sudo apt-get install -y apache2-utils
> for i in `seq 100`; do sleep .25; curl -o /dev/null -s -w %{http_code}\\n --insecure -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_noop; done
```
