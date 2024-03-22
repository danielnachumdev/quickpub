import unittest
from unittest.mock import Mock, patch
from quickpub import publish
import quickpub


def _cm(*args, **kwargs):
    return 0, b"", b""


class TestMain(unittest.TestCase):

    def setUp(self):
        quickpub.proxy.__dict__["cm"] = _cm

    @patch("quickpub.proxy.cm", new=_cm)
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
