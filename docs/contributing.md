# Contributing

```bash
>for x in $(sudo docker ps -a | awk '{print $1}'); do sudo docker kill $x >& /dev/null; sudo docker rm $x >& /dev/null; done
```

```bash
>docker run \
    --name=apidocs \
    simonsdave/ecs-apidocs \
    nginx
>cat ~/.ecs/config
[ecs]
address=0.0.0.0
port=80
log_level=info
max_concurrent_executing_http_requests=250
docker_remote_api=http://172.17.42.1:4243
>sudo docker run \
    --name=tasks \
    -v ~/.ecs/config:/root/.ecs/config \
    simonsdave/ecs-services \
    ecservice.py
>sudo docker run \
    --name=nginx \
    -p 9000:80 \
    -p 9443:443 \
    --link apidocs:apidocs \
    --link tasks:tasks \
    -v /vagrant/dhparam.pem:/etc/nginx/ssl/dhparam.pem \
    -v /vagrant/docs.ecs.cloudfeaster.com.ssl.bundle.crt:/etc/nginx/ssl/docs.crt \
    -v /vagrant/docs.ecs.cloudfeaster.com.key:/etc/nginx/ssl/docs.key \
    -v /vagrant/api.ecs.cloudfeaster.com.ssl.bundle.crt:/etc/nginx/ssl/api.crt \
    -v /vagrant/api.ecs.cloudfeaster.com.key:/etc/nginx/ssl/api.key \
    -v /vagrant/.htpasswd:/etc/nginx/.htpasswd \
    simonsdave/ecs-nginx \
    nginx.sh docs.ecs.cloudfeaster.com api.ecs.cloudfeaster.com
```

```bash
>curl -H 'Host: api.ecs.cloudfeaster.com' https://127.0.0.1:9443
```
