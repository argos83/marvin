# Custom Events Logger and Plugins

`Marvin` has a built-in event logger which is the output you see when you execute test cases, but you can add your custom `Events Logger` to handle test information and send it to a database, to a `Grafana` server or whatever you want.

If you don't want to read this, you can check it on the [examples](../examples) folder.

## Setting Up

First step is to configure the `hook_module` on `Marvin`s configuration file. Here is how it should look like:

```yaml
# marvin.yaml

hook_module: custom_logger.py
```

You need to set `hook_module` to the path of the python file that will hold the custom logger.

## Hook Format

The `hook` module is very simple and it should have the following format:

```
def main(publisher, cfg):
    pass
```

`Marvin` will try to find and execute a `main` method defined on the `hook` module and it will pass two parameters:
  * **publisher**: This is the notification object, where you can subscribe to the different events that `Marvin` produces. We will see an example later.
  * **cfg**: The current configuration that `Marvin` is handling, so you can access any value that tests have access too.

## Configuring Custom Loggers

Given that simple `hook` example, we now are going to extend that so we can subscribe to events and be notified when they are executed.

First, we are going to create a new class and then call it on `main` method:

```python
def main(publisher, cfg):
    CustomLogger(publisher, cfg)


class CustomLogger(object):
    def __init__(self, publisher, cfg):
      pass
```

Now, we are going to subscribe to some events, like when a test starts and when it finishes.

```python
from marvin.report import EventType


def main(publisher, cfg):
    CustomLogger(publisher, cfg)


class CustomLogger(object):
    def __init__(self, publisher, cfg):
        publisher.subscribe(self.on_test_started, EventType.TEST_STARTED)
        publisher.subscribe(self.on_test_ended, EventType.TEST_ENDED)

    def on_test_started(self, event):
        print("#### CUSTOM LOGGER - TEST STARTING ####")

    def on_test_ended(self, event):
        print("#### CUSTOM LOGGER- TEST ENDING ####")
```

You use the `subscribe` method on the `publisher` object to link a method with an event.

You can check the full event list and their signatures below.

To access the `config` object, you use the following syntax `cfg.marvin`. For example, if you want to know the path of the tests that are being executed, you would use the following:

```python
cfg.marvin["tests_path"]
```

## List Of Events

* SUITE_STARTED
* SUITE_ENDED
* TEST_STARTED
* TEST_ENDED
* TEST_SETUP_STARTED
* TEST_SETUP_ENDED
* TEST_ITERATION_STARTED
* TEST_ITERATION_ENDED
* TEST_TEARDOWN_STARTED
* TEST_TEARDOWN_ENDED
* STEP_STARTED
* STEP_ENDED
* STEP_SKIPPED
