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

* if a service account doesn't exists create one and
then [generate a new P12 key](https://cloud.google.com/storage/docs/authentication?hl=en#generating-a-private-key)

## Create TLS certs

* create api and docs TLS certs

> QUESTION - can [Let's Encrypt](https://letsencrypt.org/) be used to automate the
> generation of certs?

### Detour = self-signed SSL certs

```bash
> openssl genrsa -des3 -passout pass:password -out api.ecs.cloudfeaster.com.key 2048
> openssl req -new -batch -key api.ecs.cloudfeaster.com.key -passin pass:password -out api.ecs.cloudfeaster.com.csr
> mv api.ecs.cloudfeaster.com.key api.ecs.cloudfeaster.com.key.org
> openssl rsa -in api.ecs.cloudfeaster.com.key.org -passin pass:password -out api.ecs.cloudfeaster.com.key
> openssl x509 -req -days 365 -in api.ecs.cloudfeaster.com.csr -signkey api.ecs.cloudfeaster.com.key -out api.ecs.cloudfeaster.com.crt
>
> openssl genrsa -des3 -passout pass:password -out docs.ecs.cloudfeaster.com.key 2048
> openssl req -new -batch -key docs.ecs.cloudfeaster.com.key -passin pass:password -out docs.ecs.cloudfeaster.com.csr
> mv docs.ecs.cloudfeaster.com.key docs.ecs.cloudfeaster.com.key.org
> openssl rsa -in docs.ecs.cloudfeaster.com.key.org -passin pass:password -out docs.ecs.cloudfeaster.com.key
> rm docs.ecs.cloudfeaster.com.key.org
> openssl x509 -req -days 365 -in docs.ecs.cloudfeaster.com.csr -signkey docs.ecs.cloudfeaster.com.key -out docs.ecs.cloudfeaster.com.crt
```


## Manually Exploring Endpoints

```bash
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1 | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/random | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0 | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_health | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_health?quick=false | jq
> curl --insecure -s -v -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_noop | jq
```

Exploring rate limiting
```bash
> sudo apt-get install -y apache2-utils
> for i in `seq 100`; do sleep .25; curl -o /dev/null -s -w %{http_code}\\n --insecure -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1/v1.0/_noop; done
```
