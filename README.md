# quickpub
**Tested python versions**: `3.8.0`, `3.9.0`, `3.10.13`,

Example usage of how this package was published
```python
from quickpub import publish, AdditionalConfiguration, MypyRunner, PylintRunner, UnittestRunner


def main() -> None:
    publish(
        name="quickpub",
        version="0.8.0",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["twine", "danielutils"],
        min_python="3.9.19",
        config=AdditionalConfiguration(
            runners=[
                MypyRunner(),
                PylintRunner(),
                UnittestRunner(),
            ]
        )
    )


if __name__ == '__main__':
    main()

```