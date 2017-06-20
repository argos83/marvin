# Documentation

This is the main `Marvin` documentation.

## What is Marvin?

`Marvin` is a data-driven automation framework. It's main purpose is to automate test cases on a software development process but it can also be used on any repetitive task that you need to automate.

## Data-driven framework

`Marvin` test scripts are data-driven. This means that the test scripts only have the logic of the test and this logic only make sense when data is applied. Each of them have to have a `Data Provider` file associated, which will inject the data in the test script when it's executed. For now, we are just going to say that the `Test Script` and `Data Provider` files should have the same name (one a python file and the other a YAML/JSON file) and that they should be on the same folder, but later we are going to explain the different possibilities we have for the `Test Scripts` names and `Data Provider` file names.

<<<<<<< HEAD
`Marvin`'s built-in data providers are YAML and JSON, so you can create data files with these two formats. But if you need your own data provider, you can create one. Check [Data Providers](documentation/data_providers.md) documentation.
=======
`Marvin`'s built-in data providers are YAML and JSON, so you can create data files with these two formats. But if you need you own data provider, you can create one. Check [Data Providers](documentation/data_providers.md) documentation.
>>>>>>> 6aebaa8b97b46773ee45e14acc54ae17120026ee

## Directory Structure

We recommend the following directory structure when working with `Marvin` projects:

* project_name
  * **steps:** Contains all steps used on the Test Scripts
  * **test_cases:** Contains all tests of the project along with their data sources
  * **libs:** Internal or external libraries used on the test scripts _(optional)_
  * **utils:** Useful classes that might be directly related to the project, like parsing certain content, databases, etc. _(optional)_


## Test Scripts

`Test Scripts` are the base of `Marvin`'s execution process. They are structured in a way that they imitate a real life test case, and the main part are the steps involved in it.

### Test Script File

`Test Scripts` have three main methods: `setup`, `run` and `tear_down`.

Here is a basic template for a new `Test Script`:

```python
# test_cases/example_test.py
from marvin import TestScript


class TestScriptExample(TestScript):
    """Test Script Example for documentation"""

    NAME = "Test Script Example"

    def setup(self, data):
        pass

    def run(self, data):
        pass

    def tear_down(self, _data):
        pass
```

Inside this methods is where the steps are called. For example, in the `setup` method, you would call steps that open a website, create a connection to a database, and anything that would be required to set-up the test environment. On the `tear_down` method, you would close any connection to the database, logout from somewhere etc. And in the `run` method it is where you should have the main logic of your test and this method is the one that could be executed a lot of times, depending on the data defined for that test.

### Data Files

<<<<<<< HEAD
Like we said, data files are known as `Data Providers` and `Marvin` has support for YAML/JSON format automatically. But if you need your own data provider, you can create one. Check [Data Providers](documentation/data_providers.md) documentation.
=======
Like we said, data files are known as `Data Providers` and `Marvin` has support for YAML/JSON format automatically. But if you need you own data provider, you can create one. Check [Data Providers](documentation/data_providers.md) documentation.
>>>>>>> 6aebaa8b97b46773ee45e14acc54ae17120026ee

Here is a example:

```yaml
<<<<<<< HEAD
# test_cases/example_test.yaml
=======
#example_test.yaml
>>>>>>> 6aebaa8b97b46773ee45e14acc54ae17120026ee
setup:
  a_list: [1, 2]
  foo: bar

iterations:
  - arg1: iteration 1
    arg2: True

  - arg1: iteration 2
    arg2: False

tear_down:
  foo: baz
```

Data files imitates the format that `Test Script` have and they should also have three section: `setup`, `iterations` and `tear_down`.

The `setup` and `tear_down` sections matches the same as the ones on `Test Script` and the `iterations` section is a list that for every item inside that list, it will execute the `run` method on the `Test Script`.

### Test Scripts and Data Files relationship

To show you how `Marvin` links the `Test Scripts` and the `Data Files`, here is a little example following the data above:

```python
# test_cases/example_test.py
from marvin import TestScript


class TestScriptExample(TestScript):
    """Test Script Example for documentation"""

    NAME = "Test Script Example"

    def setup(self, data):
        print data["a_list"]
        print data["foo"]

    def run(self, data):
        print data["arg1"]
        print data["arg2"]

    def tear_down(self, _data):
        print data["foo"]
```

The output will be something like this:

```
[TEST] Test Script Example for documentation
    [SETUP STARTED]
[1,2]
bar
    [SETUP FINISHED - PASS]
    [ITERATION STARTED]
iteration 1
True
    [ITERATION FINISHED - PASS]
    [ITERATION STARTED]
iteration 2
False
    [ITERATION FINISHED - PASS]
    [TEARDOWN STARTED]
ba
    [TEARDOWN FINISHED - PASS]
[TEST] Test Script Example for documentation - PASS
```

## Steps

`Steps` are one of the most important things on `Marvin`. It's where the final logic of the tests takes place and when they are well designed, it could save you a lot of times when creating new `Test Scripts`.

<<<<<<< HEAD
To start with, here is a basic example of a `Step` on `Marvin`.:
=======
To start with, here is a basic example of a step:
>>>>>>> 6aebaa8b97b46773ee45e14acc54ae17120026ee

```python
from marvin import Step


class TestStep(Step):
    """Example for a simple step"""

    NAME = "Test Step"

    def run(self, params={}):
      pass
```

<<<<<<< HEAD
=======
That's the most basic template for a `Step` on `Marvin`.

>>>>>>> 6aebaa8b97b46773ee45e14acc54ae17120026ee
### Steps Status

Every `Step` by default returns `PASS` if no exception is thrown. Here is an example of a `Step` that throws an exception if a value received as parameter is odd or even and that way setting the status of it to `FAIL`:

```python
# steps/test_number.py
from marvin import Step


class NumberEvenOrOdd(Step):
    """Checks if a number is even or odd"""

    NAME = "Number Even Or Odd"

    def run(self, params={}):
      number = params.get("number")

      if number % 2:
        raise Exception("Number is not even")
```

You can also set the status of a `Step` to `Skip` by calling `self.skip()` method. For example, let's say that you have a `Step` that sets up a database connection in case there isn't one already. If there is one, then you can mark that `Step` as `Skip` and you know that the step found an existing connection.

Here is an example on how to do this:

```python
# test_step.py
from marvin import Step

from utils.db_connection import CheckDBConnection


class TestStep(Step):
    """Example for a simple step"""

    NAME = "Test Step"

    def run(self, params={}):
      if CheckDBConnection():
        self.skip("A DB Connection was already stablished")
      else:
        # Create DB connection
```

### Calling Steps

Now that we know how `Steps` are defined, we need to call them inside `Test Scripts` by using `self.step()` method.

We are going to use the example above and use that `Step`:

```python
# test_cases/example_test.py
from marvin import TestScript

from steps.test_number import NumberEvenOrOdd


class TestScriptExample(TestScript):
    """Test Script Example for documentation"""

    NAME = "Test Script Example"

    def setup(self, data):
        pass

    def run(self, data):
        # Let's pretend that the iteration receive
        # a param called "number"
        self.step(NumberEvenOrOdd).execute({
          "number": data["number"]
        })

    def tear_down(self, _data):
        pass
```

## Running Marvin (cli)

To execute `Marvin`, just run the following command:

```bash
> marvin <tests_directory>
```

So, if you have a directory called `test_cases` you would execute them like this:

```bash
> marvin test_cases
```

### Arguments

There are a few arguments you can use to customize the execution.

* **--config**: Filepath to a valid configuration file
* **--tags**: Only run tests containing any of the given tags
* **--no-tags**: Don't run tests containing any of the given tags

You can check more information running the following command:

```
> marvin ---help
```
## Configuration Values

When `Marvin` is executed, it tries to read configuration values from a config file. The workflow is the following:

1. Checks if there is a `MARVIN_CONFIG` env variable pointing to a valid path for a config file. If it exists, it loads it.
2. If that variable doesn't exists, tries to find a file named `marvin.yml`, `marvin.yaml` or `marvin.json` on the current directory. If it exists, it loads it.
3. If no configuration values are present, it loads the default values which are:
```python
'tests_path': '.',
'filter': {
    'with_tags': [],
    'without_tags': []
},
'hook_module': 'marvin_conf.py',
'env': None,
'environments': {}
```
4. Then, it checks for variables that can be overriden on the command line like `test_path`, `with_tags` and `without_tags`

As you can see, there are five possible values that you can set:

* **tests_path**: Directory where test script are saved.
* **filter**: You can setup filter by defaults instead of typing them on the `cli`
* **hook_module**: Python file that you want to hoop up to the test execution. Check more information on the [Custom Event Loggers](documentation/custom_events_logger.md) page.
