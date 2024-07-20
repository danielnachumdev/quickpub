from danielutils import RetryExecutor, ExponentialBackOffStrategy, ConstantBackOffStrategy
from requests import Response

from proxy import get  # type: ignore
from quickpub import Version
from ...constraint_enforcer import ConstraintEnforcer


class RemoteVersionEnforcer(ConstraintEnforcer):
    _HTTP_FAILED_MESSAGE: str = "Failed to send http request"

    def enforce(self, name: str, version: Version, demo: bool = False, **kwargs) -> None:  # type: ignore
        if demo:
            return
        url = f"https://pypi.org/project/{name}/"

        timeout_strategy = ExponentialBackOffStrategy(1.1, 1.5)

        def wrapper() -> Response:
            return get(url, timeout=timeout_strategy.get_backoff())

        executor: RetryExecutor[Response] = RetryExecutor(ConstantBackOffStrategy(1))
        response = executor.execute(wrapper, 5)
        if response is None:
            raise SystemExit(self._HTTP_FAILED_MESSAGE)
        html = response.content.decode()
        i = html.index(f" {name} ")
        try:
            remote_version = Version.from_str(html[i:i + 50].splitlines()[0].strip().split()[1])
        except Exception as e:
            raise SystemExit(f"{self.__class__.__name__} encountered an unexpected error while parsing.") from e
        if not version > remote_version:
            raise SystemExit(
                f"Specified version is '{version}' but (remotely available) latest existing is '{remote_version}'")


__all__ = [
    'RemoteVersionEnforcer'
]
