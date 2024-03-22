# quickpub

Example usage of how this package was published
```python
from quickpub import publish


def main() -> None:
    publish(
        name="quickpub",
        version="0.5.2",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        keywords=["Utils", "PyPi", "Publish", "Quick"],
        dependencies=["twine", "danielutils"]
    )


if __name__ == "__main__":
    main()
```