"""Base test classes for centralized test inheritance.

This module provides base test classes that centralize the inheritance
from danielutils test classes, making it easier to manage test infrastructure.

Note: These classes do NOT inherit from AutoCWDTestCase/AsyncAutoCWDTestCase
to avoid leaving residual files in the project directory. Instead, use
temporary_test_directory() context manager from tests.test_helpers.
"""

import unittest

from danielutils import (
    AlwaysTeardownTestCase,
    AsyncAlwaysTeardownTestCase,
)


class BaseTestClass(AlwaysTeardownTestCase):
    """Base test class for synchronous unit tests.

    This class provides a centralized base for all synchronous tests.
    It does NOT use AutoCWDTestCase to avoid leaving residual files.
    Use temporary_test_directory() context manager for temporary directories.
    """

    pass


class AsyncBaseTestClass(AsyncAlwaysTeardownTestCase):
    """Base test class for asynchronous unit tests.

    This class provides a centralized base for all asynchronous tests.
    It does NOT use AsyncAutoCWDTestCase to avoid leaving residual files.
    Use temporary_test_directory() context manager for temporary directories.
    """

    pass
