
## What is Marvin?

`Marvin` is a data-driven framework designed for integration/system/E2E testing. Most available testing frameworks are
designed for unit testing, and don't provide enough tooling to code, track, and report what occurs within a single test
case, since there's no need to do so for unit tests.

## Data-driven framework

Although `Marvin` supports running tests with no data sets, you can get the most of it by creating data-driven tests.
This means that the test scripts only have the logic of the test and this logic gets executed one or many times as data
is applied. Each test has a `Data Provider` which will inject the data in the test script when
it's executed. Marvin supports by default YAML/JSON data providers. For now, we are just going to say that the
`Test Script` and `Data` files should have the same prefix (one a python file and the other a YAML/JSON file) and that
they should be in the same directory, but later we are going to explain the different possibilities we have for the
`Test Scripts` names and `Data` file names.

`Marvin`'s built-in data providers are YAML and JSON, so you can create data files with these two formats. But if you
need your own data provider, you can create one. Check [Data Providers](data_providers.md) documentation.

## Directory Structure

We recommend the following directory structure when working with `Marvin` projects:

* project_name
  * **steps:** Contains all steps used on the Test Scripts
  * **test_cases:** Contains all tests of the project along with their data sources
  * **libs:** Internal or external libraries used on the test scripts _(optional)_
  * **utils:** Useful classes that might be directly related to the project, like parsing certain content, databases,
  etc. _(optional)_


## Test Scripts

`Test Scripts` are the base of `Marvin`'s execution process. They are structured in a way that they resemble a manual
test case definition, and the actual implementation is abstracted in steps.

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

Inside this methods is where the steps are called. For example, in the `setup` method, you would call steps that open
a website, create a connection to a database, or anything that would be required to set-up the test environment or any
required preconditions.
In the `run` method it is where you should place the main logic of your test and this method is the one that can be
executed one or more times, depending on the data defined for that test.
In the `tear_down` method, you would close any connection to the database, logout, or perform any clean up tasks.

### Data Files

As we said, data files are consumed by `Data Providers` and `Marvin` has support for YAML/JSON format out of the box.
(if you need a different data source, you can create one your own [data provider](data_providers.md)).


Here is a example:

```yaml
# test_cases/example_test.yaml
setup_data:
  username: admin-test
  password: hunter2

iterations:
  - data:
      create_user:
        name: John Iteration 1
        account_type: viewer
      should_succeed: True

  - data:
      create_user:
        name: Mary Iteration 2
        account_type: reporter
      should_succeed: True

  - data:
      create_user:
        name: George Iteration 3
        account_type: admin
      should_succeed: False

tear_down_data:
  logout: true
```

The data file format resembles the structure that `Test Script` has and it can also have three sections: `setup`,
`iterations` and `tear_down`.

The `setup` and `tear_down` sections matches the same as the ones on `Test Script`. And the `iterations` section is a
list that will define how many times and with which data the `run` method on the `Test Script` is executed.

Learn more about [data files](data_files.md)

### Test Scripts and Data Files relationship

To show you how `Marvin` links the `Test Scripts` and the `Data Files`, here is a little example following the data
above:

```python
# test_cases/example_test.py
from marvin import TestScript


class CreateUser(TestScript):
    """Step for creating a user specifying a user type"""

    NAME = "Create User"

    def setup(self, data):
        print("Using username {}".format(data["username"]))
        print("Using password {}".format(data["password"]))

    def run(self, data):
        print("Creating user '{}' as '{}'".format(
          data["create_user"]["name"], data["create_user"]["account_type"]
        ))

    def tear_down(self, _data):
        print("Should we logout? {}".format(data["logout"]))
```

The output will look like this:

```
[TEST] Test Script Example for documentation
    [SETUP STARTED]
Using username admin-test
Using password hunter2
    [SETUP FINISHED - PASS]
    [ITERATION STARTED]
Creating user 'John Iteration 1' as 'viewer'
    [ITERATION FINISHED - PASS]
    [ITERATION STARTED]
Creating user 'Mary Iteration 2' as 'reporter'
    [ITERATION FINISHED - PASS]
    [ITERATION STARTED]
Creating user 'George Iteration 3' as 'admin'
    [ITERATION FINISHED - PASS]
    [TEARDOWN STARTED]
Should we logout? True
    [TEARDOWN FINISHED - PASS]
[TEST] Test Script Example for documentation - PASS
```

## Steps

`Steps` are the core entities in `Marvin`. It's where the actual logic of the tests takes place, and when they are well
designed, they will save you a lot of time when creating new `Test Scripts` or maintaining existing tests.

To start with, here is a (very) basic example of a `Step` in `Marvin`.:

```python
from marvin import Step


class TestStep(Step):
    """Example for a simple step"""

    NAME = "Test Step"

    def run(self, param1, param2):
      pass
```

### Step Status

Every `Step` by default returns `PASS` if no exception is raised. Here is an example of a `Step`, following the data
above, that makes a login of a user and if the login wasn't successful it raises an exception making the step status
flagged as `FAIL`:

```python
# steps/login_with_user.py
from marvin import Step

from libs.my_api_lib import authenticate


class LoginWithUser(Step):
    """Makes a login with a specific user"""

    NAME = "Login With User"

    def run(self, username, password):
      # Here you could do some checks before doing the actual login
      # like format of the username, length of password, etc.

      session = authenticate(username, password)
      assert session.is_active(), "Unable to login"
      return session
```

In the example, an `AssertionError` could be raised, but any other exception will result in the step failing.


### Calling Steps

Now that we know how `Steps` are defined, we need to call them inside `Test Scripts` by using `self.step()` method.

We are going to use the example above and use that `Step`:

```python
# test_cases/example_test.py
from marvin import TestScript

from steps.login_with_user import LoginWithUser


class CreateUser(TestScript):
    """Step for creating a user specifying a user type"""

    NAME = "Create User"

    def setup(self, data):
        self.step(LoginUser).execute(data["username"], data["password"])

    def run(self, data):
        ...

    def tear_down(self, data):
        ...
```

Ideally, steps should have a single responsibility, i.e. if you end up with a step called `CreateCartAndPay` you should
probably split that into two steps to improve re-usability, tracing, and reporting. 

However, you can also invoke steps from within other steps which allows you to create macro steps while sticking to the
single responsibility principle. For example:

```python
# steps/macros/make_purchase.py
from marvin import Step

from steps.create_cart import CreateCart
from steps.select_shipping_method import SelectShippingMethod
from steps.pay_order import PayOrder

class MakePurchase(Step):
    """Step for completing a purchase"""

    NAME = "Make Purchase"

    def run(self, items, shipping_method, credit_card):
        order = self.step(CreateCart).execute(items)

        self.step(SelectShippingMethod).execute(order, shipping_method)

        receipt = self.step(PayOrder).execute(order, credit_card)

        return order, receipt
```

`Marvin` also allows you to alter the way a `Step` is executed in order to obtain different results. What if you want to
use the `LoginWithUser` step in a negative test case so it passes only if it raises an `AuthenticationError`?.
See [Steps invocation methods](steps.md#invocation-methods) to learn how to achieve this.


## Running Marvin (CLI)

To execute `Marvin`, just run the following command:

```bash
> marvin <tests_directory>
```

So, if you have a directory called `test_cases` you would execute them like this:

```bash
> marvin test_cases
```

### CLI Arguments

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

1. Checks if a config path was passed via the `--config` cli arg.
2. Checks if there is a `MARVIN_CONFIG` env variable pointing to a valid path for a config file. If it exists, it loads
it.
3. If that variable doesn't exists tries to find a file named `marvin.yml`, `marvin.yaml` or `marvin.json` in the
current directory. If it exists, it loads it.
4. If no configuration values are present, it loads the default values which are:
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
5. Then, it checks for variables that can be overriden on the command line like `test_path`, `with_tags` and
`without_tags`.

As you can see, there are five possible values that you can set:

* **tests_path**: Directory where test script are saved.
* **filter**: You can setup default filters instead of typing them in the `cli`.
* **hook_module**: Python file that you want to hoop up to the test execution. Read more about this on the
[Custom Event Loggers and Plugins](custom_events_logger.md) page.
* **env** and **environments**: Define where to load the environment specific configuration (e.g. endpoints,
credentials, etc). This is to support running your tests against multiple environments (e.g. local, dev, staging). Read
more on the [Environment Configuration](environments.md) page.