# Change Log
All notable changes to this project will be documented in this file.
Format of this file follows [these](http://keepachangelog.com/) guidelines.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.9.0] - [2016-05-01]

### Changed

- bump API version from v1.0 -> v1.1
- removed required 'tag' property from POST to /tasks endpoint; use the
  image name format 'owner/image:tag' format to specify a specific, tagged
  version of an image; image names not in this format will result in a
  400 (Bad Request) response

### Removed

- ...

## [0.8.0] - [2015-05-10]

- not really the initial release but intro'ed CHANGELOG.md late
- initial clf commit to github was 25 Jan '16
