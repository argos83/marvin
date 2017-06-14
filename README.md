# Marvin - Python Test Automation Framework

Marvin is a data-driven framework designed for automating test cases. Includes features like `cli` runner and reporter, JSON/YAML support for data sources with option to implement your own parser, tests environment configuration (dev, staging, prod, etc), customs reporters and much more.

## Installation

Just like any other `PyPi` package, run the following command:

```bash
> pip install marvin-framework
```

To check if it's installed correctly, run the `marvin --help` command and it should give you something like this:

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
