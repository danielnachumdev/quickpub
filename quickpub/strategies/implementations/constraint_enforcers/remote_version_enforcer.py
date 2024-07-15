import requests

from quickpub import Version
from ...constraint_enforcer import ConstraintEnforcer

class RemoteVersionEnforcer(ConstraintEnforcer):
    def enforce(self, name: str, version: str, demo: bool, **kwargs) -> None:  # type: ignore
        if demo:
            return
        local_version = Version.from_str(version)
        url = f"https://pypi.org/project/{name}/"
        response = requests.get(url, timeout=1)
        html = response.content.decode()
        i = html.index(f" {name} ")
        try:
            remote_version = Version.from_str(html[i:i + 50].splitlines()[0].strip().split()[1])
        except:
            raise SystemExit(f"{self.__class__.__name__} encountered an unexpected error while parsing.")
        if not local_version > remote_version:
            raise SystemExit(
                f"Specified version is '{local_version}' but (remotely available) latest existing is '{remote_version}'")


__all__ = [
    'RemoteVersionEnforcer'
]
