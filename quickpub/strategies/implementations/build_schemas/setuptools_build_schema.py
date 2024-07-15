from typing import Literal

from danielutils import info, file_exists

from ...build_schema import BuildSchema


class SetuptoolsBuildSchema(BuildSchema):
    def __init__(self, setup_file_path: str = "./setup.py", backend: Literal["toml"] = "toml") -> None:
        self._backend = backend
        self._setup_file_path = setup_file_path

    def build(self, verbose: bool = False, *args, **kwargs) -> None:
        from quickpub.proxy import cm
        if not file_exists(self._setup_file_path):
            raise self.EXCEPTION_TYPE(f"Could not find {self._setup_file_path} file")
        if verbose:
            info("Creating new distribution...")
        ret, stdout, stderr = cm("python", self._setup_file_path, "sdist")
        if ret != 0:
            raise self.EXCEPTION_TYPE(stderr.decode(encoding="utf8"))


__all__ = [
    "SetuptoolsBuildSchema",
]
