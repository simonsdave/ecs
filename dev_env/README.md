# Development Environment

To increase predicability, it is recommended
that ecs development be done on a [Vagrant](http://www.vagrantup.com/) provisioned
[VirtualBox](https://www.virtualbox.org/)
VM running [Ubuntu 14.04](http://releases.ubuntu.com/14.04/).
Below are the instructions for spinning up such a VM.

Spin up a VM using [create_dev_env.sh](create_dev_env.sh)
(instead of using ```vagrant up``` - this is the only step
that standard vagrant commands aren't used - after provisioning
the VM you will use ```vagrant ssh```, ```vagrant halt```,
```vagrant up```, ```vagrant status```, etc).

```bash
>./create_dev_env.sh simonsdave simonsdave@gmail.com ~/.ssh/id_rsa.pub ~/.ssh/id_rsa
Bringing machine 'default' up with 'virtualbox' provider...
==> default: Importing base box 'trusty'...
.
.
.
```

SSH into the VM.

```bash
>vagrant ssh
Welcome to Ubuntu 14.04.5 LTS (GNU/Linux 3.13.0-98-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

  System information as of Mon Sep 18 11:40:32 UTC 2017

  System load:  0.49              Processes:           82
  Usage of /:   3.5% of 39.34GB   Users logged in:     0
  Memory usage: 6%                IP address for eth0: 10.0.2.15
  Swap usage:   0%

  Graph this data and manage this system at:
    https://landscape.canonical.com/

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

0 packages can be updated.
0 updates are security updates.

New release '16.04.3 LTS' available.
Run 'do-release-upgrade' to upgrade to it.

~>
```

Start the ssh-agent in the background.

```bash
~> eval "$(ssh-agent -s)"
Agent pid 25657
~>
```

Add SSH private key for github to the ssh-agent

```bash
~> ssh-add ~/.ssh/id_rsa_github
Enter passphrase for /home/vagrant/.ssh/id_rsa_github:
Identity added: /home/vagrant/.ssh/id_rsa_github (/home/vagrant/.ssh/id_rsa_github)
~>
```

Clone the repo.

```bash
~> git clone git@github.com:simonsdave/ecs.git
Cloning into 'ecs'...
remote: Counting objects: 2430, done.
remote: Total 2430 (delta 0), reused 0 (delta 0), pack-reused 2430
Receiving objects: 100% (2430/2430), 1.79 MiB | 1.65 MiB/s, done.
Resolving deltas: 100% (1647/1647), done.
Checking connectivity... done.
~>
```

Install all pre-reqs.

```bash
~> cd ecs
~/ecs> source cfg4dev
New python executable in env/bin/python
.
.
.
~/ecs>
```

Run all unit & integration tests.

```bash
(env)~/ecs> tor_async_util_nosetests.py --with-coverage --cover-branches --cover-erase --cover-package ecs
........................................................................
Name                             Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------------
ecs/async_actions.py               141      0     16      0   100%
ecs/async_docker_remote_api.py     274      0     32      0   100%
ecs/jsonschemas.py                   8      0      0      0   100%
ecs/main.py                         56      0      2      0   100%
ecs/request_handlers.py             55      0      8      0   100%
------------------------------------------------------------------
TOTAL                              534      0     58      0   100%
----------------------------------------------------------------------
Ran 72 tests in 117.877s

OK
(env)~/ecs>
```
