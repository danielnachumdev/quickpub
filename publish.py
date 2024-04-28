from quickpub import publish, AdditionalConfiguration, MypyRunner, PylintRunner, UnittestRunner


def main() -> None:
    publish(
        name="quickpub",
        version="0.8.3",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["twine", "danielutils"],
        min_python="3.8.0",
        config=AdditionalConfiguration(
            runners=[
                MypyRunner(bound="<15", configuration_path="./mypy.ini"),
                PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
                UnittestRunner(bound=">=0.8"),
            ]
        )
    )


if __name__ == '__main__':
    main()
