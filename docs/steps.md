## Steps

### Invocation methods


 * **safely**: Pending

 * **expect_exception**: Pending

 * **do_not_fail**: Pending

### Extending steps via context managers

Pending

### Tagging

Pending

### Skipping tests from steps

As mentioned in the [basic guide](main.md#step-status), a `Step` status is `PASS` if doesn't raise any exception or
`FAIL` otherwise (this behavior can be modified via the different [invocation methods](#invocation-methods) though).
You can also set the status of a `Step` to `SKIP` by calling `self.skip()` method. As result of this, the test case (if
this occurred in the context of the `setup` or `tear_down` methods) or the current iteration (if this occurred in the
context of the test script's `run` method) will be skipped as well.

You could use this when certain steps or tests do not apply for a specific environment or version of the SUT.

For example:

```python
# add_to_wishlist.py
from marvin import Step

class AddItemToWishlist(Step):
    """Adds an item to the user's wishlist"""

    NAME = "Add to wishlist"

    def run(self, session, item):
      if self.cfg.features['wishlist']['supported']:
        self.skip("Wishlist is not supported in environment %s" % self.cfg.environment)
      else:
        session.profile.whishlist.add(item)
```