# Sanity Tests

Sanity tests verify end-to-end functional correctness
of an existing deployment. The existing deployment is
assumed to be a cloud hosted ECS deployment.

A complete set of sanity tests is comprised of the
[integration test suite](../integration) plus the tests
in this directory. The integration tests are designed
to be run against a local ECS development environment as
well as a cloud hosted ECS deployment although these
tests focus on ECS service functionality rather than 
verifying the max permitted request size. The later
kind of tests is what the sanity tests in this directory
tend to focus on.

The bash commands below demonstrate how to run the sanity
tests against a cloud hosted ECS deployment.

```bash
>git clone https://github.com/simonsdave/ecs.git
>cd ecs
>source cfg4dev
>cd tests
>ECS_ENDPOINT=https://api.ecs.cloudfeaster.com \
    ECS_KEY=04710f3549854a02b93d2098596195aa \
    ECS_SECRET=41b08e0a753c8b328428a53da4049503 \
    nosetests
```
