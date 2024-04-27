from quickpub import publish, StaticAnalyzersConfig, AdditionalConfiguration, TestingConfiguration


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
            analyzers=[
                StaticAnalyzersConfig("pylint", config_file_path="./.pylintrc"),
                StaticAnalyzersConfig("mypy", config_file_path="./mypy.ini")
            ],
            testers=[
                TestingConfiguration("unittest", "./tests")
            ]
        )
    )


if __name__ == '__main__':
    main()
