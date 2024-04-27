from quickpub import publish


def main() -> None:
    publish(
        name="quickpub",
        version="0.7.0",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["twine", "danielutils"],
        min_python="3.9.19"
    )


if __name__ == '__main__':
    main()
