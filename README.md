# Marvin - Python Test Automation Framework

`Marvin` is a data-driven framework designed for integration/system/E2E testing.
Most available testing frameworks are designed for unit testing, and don't provide enough tooling to code, track, and report what occurs within a single test case, since there's no need to do so for unit tests.

Marvin provides a step abstraction layer which allow system tests projects to:

* Write readable test cases which resemble manual test cases.
* Abstract in steps all the individual actions that occur in a test case, so they can be individually tracked, measured, and reported.
* Reuse steps among different test cases and even test projects.
* Compound multiple steps into macro steps.

Marvin is highly extensible and configurable. This allows users to:

* Implement test data source providers (JSON/YAML already supported by marvin).
* Create their own reports: e.g. generate HTML reports, or post results to Splunk or ElasticSearch.
* Create plug-ins to ortogonally extend the power of test cases. Tests code should only deal with the business logic of the SUT, they shouldn't have to handle logic like taking screenshots, uploading crash dumps, etc. Why not let a plugin take care of that?
* Easily create environment configuration (for your dev, staging, and prod environments)

## Installation

Just like any other `PyPi` package, run the following command:

```bash
> pip install marvin-test
```

To check if it's installed correctly, run the `marvin --help` command. The output should look like this:

```
$ marvin --help
usage: marvin [-h] [--config CONFIG] [--tags [WITH_TAGS [WITH_TAGS ...]]]
              [--no-tags [WITHOUT_TAGS [WITHOUT_TAGS ...]]]
              [DIRECTORY]

Marvin test runner

positional arguments:
  DIRECTORY             root directory containing tests

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        path to config file
  --tags [WITH_TAGS [WITH_TAGS ...]]
                        only run tests containing any of the given tags
  --no-tags [WITHOUT_TAGS [WITHOUT_TAGS ...]]
                        don't run tests containing any of the given tags
```
## Documentation

Checkout the full [documentation](documentation/main.md).
