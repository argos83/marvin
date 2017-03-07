import os
import sys

import pytest


def pytest_configure(config):
    """Path hack to allow tests to import Marvin"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture()
def ctx():
    from tests.stubs import DummyContext
    return DummyContext()