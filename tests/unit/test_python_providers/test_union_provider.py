from unittest.mock import AsyncMock, MagicMock

from quickpub.strategies.implementations.python_providers.union_provider import (
    UnionProvider,
)

from tests.base_test_classes import AsyncBaseTestClass


class TestUnionProvider(AsyncBaseTestClass):
    async def test_import_succeeds(self) -> None:
        self.assertIsNotNone(UnionProvider)

    async def test_yields_envs_from_all_child_providers_in_order(self) -> None:
        provider_a = MagicMock()
        provider_a.__aiter__ = MagicMock(
            return_value=self._async_iter([("env-a", AsyncMock()), ("env-b", AsyncMock())])
        )
        provider_b = MagicMock()
        provider_b.__aiter__ = MagicMock(
            return_value=self._async_iter([("env-c", AsyncMock())])
        )

        results = []
        async for env_name, executor in UnionProvider([provider_a, provider_b]):
            results.append(env_name)

        self.assertEqual(["env-a", "env-b", "env-c"], results)

    async def _async_iter(self, items):
        for item in items:
            yield item
