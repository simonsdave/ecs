# Development Environment

To increase predicability, it is recommended
that ecs development be done on a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 14.04](http://releases.ubuntu.com/14.04/).
Below are the instructions for spinning up such a VM.

Spin up a VM using [create_dev_env.sh](create_dev_env.sh)
(instead of using ```vagrant up```).

```bash
>./create_dev_env.sh
github username> simonsdave
github email> simonsdave@gmail.com
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'trusty'...
.
.
.
```

SSH into the VM.

```bash
>vagrant ssh
Welcome to Ubuntu 14.04 LTS (GNU/Linux 3.13.0-27-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

 System information disabled due to load higher than 1.0

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

0 packages can be updated.
0 updates are security updates.


vagrant@vagrant-ubuntu-trusty-64:~$
```

Clone the ecs repo.

```bash
vagrant@vagrant-ubuntu-trusty-64:~$ git clone https://github.com/simonsdave/ecs.git
Cloning into 'ecs'...
remote: Counting objects: 519, done.
remote: Compressing objects: 100% (99/99), done.
remote: Total 519 (delta 48), reused 0 (delta 0), pack-reused 416
Receiving objects: 100% (519/519), 96.20 KiB | 0 bytes/s, done.
Resolving deltas: 100% (290/290), done.
Checking connectivity... done.
vagrant@vagrant-ubuntu-trusty-64:~$
```

Install all pre-reqs.

```bash
vagrant@vagrant-ubuntu-trusty-64:~$ cd ecs
vagrant@vagrant-ubuntu-trusty-64:~/ecs$ source cfg4dev
New python executable in env/bin/python
Installing setuptools, pip...done.
.
.
.
```

Run all unit & integration tests.

```bash
(env)vagrant@vagrant-ubuntu-trusty-64:~/ecs$ coverage erase
(env)vagrant@vagrant-ubuntu-trusty-64:~/ecs$ tor_async_util_nosetests.py --with-coverage
.............................................................S
Name                             Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------------
ecs/async_actions.py               135      0     14      0   100%
ecs/async_docker_remote_api.py     240      1     22      0    99%   124
ecs/jsonschemas.py                   8      0      0      0   100%
ecs/request_handlers.py             49      0      6      0   100%
----------------------------------------------------------------------------
TOTAL                              432      1     42      0    99%
----------------------------------------------------------------------
Ran 62 tests in 172.234s

OK (SKIP=1)
(env)vagrant@vagrant-ubuntu-trusty-64:~/ecs$
```
