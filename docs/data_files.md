# Data Files

## Naming and location

When starting a test, `Marvin` will search for the test data. By default YAML/JSON formats are supported, so if your
test script filename is `example_test.py` then the following would be valid data file names for that test:
`example_test.yaml`, `example_test.dataset1.yml`, `example_test.json`, `example_test.other-dataset.json`, etc.

The data files must be in the same directory than the test script file, or in a deeper directory, but not outside. Also,
Marvin will skip any test or data when located in a directory whose name starts with `.` (e.g. `.pending_tests/`)
For instance, the tests directory structure could look like this:

```
test_cases/
├── shopping-cart/
│   ├── test_cart_creation.py
│   ├── test_cart_creation.yaml
│   ├── test_shipping_options.py
│   ├── test_shipping_options.local.yaml
│   └── test_shipping_options.international.yaml
└── payment/
    ├── test_pay_order.py
    ├── paypal/
    │   ├── test_pay_order.paypal-no-balance.yaml
    │   └── test_pay_order.paypal-full-credit.yaml
    ├── card/
    │   ├── test_pay_order.debit.yaml
    │   └── test_pay_order.credit.yaml
    └── .bitcoin/
        └── test_pay_order.bitcoin-work-in-progress.yaml    
```

## File content structure

Here is how the data file should be structured, in this documentation we'll use YAML format for the examples. The JSON
format has the same structure and the keys have the same names.

The root element is an object (i.e. it would be mapped to a python dictionary). All the fields are optional (however an
empty data file would result in no iterations being run, so it doesn't make much sense).


```yaml
# test_cases/user_creation_test.yaml
name: Create Users Suite 1
description: Verifies creation of users with different access levels

tags: ['module:users', 'e2e-suite']

setup_data:
  username: admin-test
  password: hunter2

iterations:
  - name: Viewer user
    data:
      create_user:
        name: John
        account_type: viewer
        projects: ['project1', 'project2']

  - tags: [regression]
    data:
      create_user:
        name: Mary
        account_type: reporter

  - data:
      create_user:
        name: George
        account_type: admin

tear_down_data:
  drop_database: true
```

**Fields**:

 * **name**: [`string`] Overrides the default name of the test (defined in the test script). You could have a very
generic test script, and let the different data file define what's the name of the test that shows up in the reports.
 * **description**: [`string`] similar to `name`, but it overrides the default test description
 * **tags**: [`array of strings`] extends the set of test tags (defined in the test script), so they can be use for
execution filtering or reporting purposes. In the example above, all the data set related to the "users module" of the
SUT could be tagged with `module:users` and a handful of data files could be tagged with `e2e-suite`. So from the CLI
you could execute `marvin --tags module:users`, or `marvin --tags e2e-suite`, or `marvin --tags module:user e2e-suite`
to respectively run all the tests related to the users module, all the tests that are in the end to end suite, or all
the tests related to the users module that are also part of the end to end suite.
 * **setup_data**: [`any`] if defined, whatever content under this key will be passed to the `setup` method of your
test script.
 * **iterations**: [`array of iteration objects`] For each entry in this list the `run` method of your test script will
be invoked. The structure of each item is described below.
 * **iterations.[n].name**: [`string`] If defined, will be shown in the reports as the name of the iteration.
 * **iterations.[n].description**: [`string`] A description for the iteration.
 * **iterations.[n].tags**: [`array of string`] You can tag individual iterations too. In the example above, if you run
the CLI command `marvin --tags regression` the first and third iterations will not be executed.
 * **iterations.[n].data**: [`any`] if defined, whatever content under this key will be passed to the `run` method of
your test script.
 * **tear_down_data**: [`any`] if defined, whatever content under this key will be passed to the `tear_down` method of
your test script.

## Other file formats and data sources

If you wish, you can implement your own `DataProvider`, for instance, to get test case data from XML files (puaj), a
database, or even from a random data generator. Refer to the [Data Providers](data_providers.md) page to learn how to.