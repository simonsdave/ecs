# Change Log

All notable changes to this project will be documented in this file.
Format of this file follows [these](http://keepachangelog.com/) guidelines.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.9.1] - [2016-05-xx]

### Added

- deployment configuration used with ```ecsctl.sh dep create``` now permits
  optional configuration of:
    - TLS versions and ciphers - see ```tls_versions``` and ```tls_ciphers```
      properties of the deployment configuration file - by default these 
      are set using [Mozilla's Security/Server Side TLS](https://wiki.mozilla.org/Security/Server_Side_TLS)
      ```nginx``` and ```modern``` settings which presents a good security
      posture but might prove problematic for some clients
    - version of the ECS docker images to be deployed - see
      ```ecs_docker_image_version``` property in the deployment configuration
      file - by default the images tagged with ```latest``` are deployed

### Changed

- tornado 4.5 -> 4.5.2
- pep8 1.7.0 -> 1.7.1

### Removed

- ...

## [0.9.0] - [2016-05-01]

### Changed

- bump API version from v1.0 -> v1.1
- removed required 'tag' property from POST to /tasks endpoint; use the
  image name format 'owner/image:tag' format to specify a specific, tagged
  version of an image; image names not in this format will result in a
  400 (Bad Request) response

## [0.8.0] - [2015-05-10]

- not really the initial release but intro'ed CHANGELOG.md late
- initial clf commit to github was 25 Jan '16
