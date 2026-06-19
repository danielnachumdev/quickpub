import logging
from typing import List, Set, Tuple

from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...python_provider import PythonProvider

logger = logging.getLogger(__name__)


class UnionProvider(PythonProvider):
    def __init__(self, providers: List[PythonProvider]) -> None:
        requested_envs = [env for provider in providers for env in provider.requested_envs]
        PythonProvider.__init__(
            self,
            requested_envs=requested_envs,
            explicit_versions=[],
            exit_on_fail=any(provider.exit_on_fail for provider in providers),
        )
        self.providers = providers
        self._child_index = 0
        self._child_iterator = None
        logger.info(
            "Initialized UnionProvider with %d child providers", len(providers)
        )

    def get_python_executable_name(self) -> str:
        if not self.providers:
            raise RuntimeError("UnionProvider has no child providers")
        return self.providers[0].get_python_executable_name()

    async def __anext__(self) -> Tuple[str, AsyncLayeredCommand]:
        while self._child_index < len(self.providers):
            if self._child_iterator is None:
                self._child_iterator = self.providers[self._child_index].__aiter__()

            try:
                return await self._child_iterator.__anext__()
            except StopAsyncIteration:
                self._child_index += 1
                self._child_iterator = None

        raise StopAsyncIteration

    async def _get_available_envs_impl(self) -> Set[str]:
        available_envs: Set[str] = set()
        for provider in self.providers:
            available_envs.update(await provider._get_available_envs())
        return available_envs


__all__ = ["UnionProvider"]
