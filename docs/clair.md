# [Clair](https://github.com/coreos/clair)

# Get Postgres Running & Create Database

* from [here](https://hub.docker.com/_/postgres/) get the Postgres Docker image
downloaded, spin up Postgres in the the background and create
a database called ```clair```

```
>sudo docker pull postgres:9.5.2
>sudo docker run --name postgres -p 5432:5432 -d postgres:9.5.2
>sudo docker run --rm --link postgres:postgres postgres:9.5.2 sh -c 'echo "create database clair" | psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
```

# Get Clair Running

* from [here](https://github.com/coreos/clair#docker)
* [this](http://www.postgresql.org/docs/9.5/static/libpq-connect.html#LIBPQ-CONNSTRING) is a good reference on Postgres connection strings

```bash
>mkdir $HOME/clair_config
>curl -L https://raw.githubusercontent.com/coreos/clair/master/config.example.yaml -o $HOME/clair_config/config.yaml
>sed -i -e 's|source:|source: postgresql://postgres@postgres:5432/clair?sslmode=disable|g' $HOME/clair_config/config.yaml
```

```bash
>sudo docker pull quay.io/coreos/clair:latest
>sudo docker run -d --name clair -p 6060-6061:6060-6061 --link postgres:postgres -v /tmp:/tmp -v $HOME/clair_config:/config quay.io/coreos/clair:latest -config=/config/config.yaml
>sudo docker logs -f clair
2016-05-10 20:26:18.474932 I | pgsql: running database migrations
goose: migrating db environment '', current version: 0, target: 20151222113213
OK    20151222113213_Initial.sql
2016-05-10 20:26:18.538001 I | pgsql: database migration ran successfully
2016-05-10 20:26:18.538449 I | notifier: notifier service is disabled
2016-05-10 20:26:18.538548 I | api: starting main API on port 6060.
2016-05-10 20:26:18.539300 I | api: starting health API on port 6061.
2016-05-10 20:26:18.539467 I | updater: updater service started. lock identifier: 3646a258-4790-46bb-9920-3f78eac38ea5
2016-05-10 20:26:18.547877 I | updater: updating vulnerabilities
2016-05-10 20:26:18.547941 I | updater: fetching vulnerability updates
2016-05-10 20:26:18.548006 I | updater/fetchers/ubuntu: fetching Ubuntu vulnerabilities
2016-05-10 20:26:18.558202 I | updater/fetchers/debian: fetching Debian vulnerabilities
2016-05-10 20:26:18.559953 I | updater/fetchers/rhel: fetching Red Hat vulnerabilities
2016-05-10 20:35:03.196968 I | updater: adding metadata to vulnerabilities
2016-05-10 20:58:01.376653 I | updater: update finished
^C>
```

* install [analyze-local-images](https://github.com/coreos/clair/tree/master/contrib/analyze-local-images) - a
quick warning = ```go get``` often creates a "Segmentation fault" - if this happens try running 
the ```go get``` again and it should complete as expected

```bash
>sudo apt-get install -y gccgo-go
>mkdir $HOME/gopath
>export GOPATH=$HOME/gopath
>export PATH="$GOPATH/bin:$PATH"
>go get -u github.com/coreos/clair/contrib/analyze-local-images
```

* run ```analyze-local-images```

```bash
>sudo $GOPATH/bin/analyze-local-images simonsdave/ecs-services:latest
```

# Other Stuff

* [Clair Setup](https://tectonic.com/quay-enterprise/docs/1.16.0/clair.html)

* from [here](https://github.com/wemanity-belgium/hyperclair) on hyperclair

```bash
>sudo curl -L -o /usr/local/bin/hyperclair  https://github.com/wemanity-belgium/hyperclair/releases/download/0.5.0/hyperclair-linux-amd64
>sudo chmod a+x /usr/local/bin/hyperclair
>cat ~/.hyperclair.yml
```

* spin up a local docker registry per [these](https://docs.docker.com/registry/deploying/) instructions

```bash
>sudo docker pull registry:2
>sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
