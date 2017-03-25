from tests.stubs import DummyTest


def test_test_basic(ctx):
    """Verify a basic test operation"""
    ctx.test(DummyTest).execute()
