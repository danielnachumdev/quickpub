import unittest
from unittest.mock import Mock
from quickpub import publish
import danielutils


class TestMain(unittest.TestCase):
    def setUp(self):
        self.cm_mock = Mock()
        danielutils.cm = self.cm_mock

    def test_main(self):
        publish(
            name="quickpub",
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["twine", "danielutils"]
        )
