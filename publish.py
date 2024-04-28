from quickpub import publish, AdditionalConfiguration, MypyRunner, PylintRunner, UnittestRunner


def main() -> None:
    publish(
        name="quickpub",
        version="0.8.1",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["twine", "danielutils"],
        min_python="3.8.0",
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
