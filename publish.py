from quickpub import publish, AdditionalConfiguration, MypyRunner, PylintRunner, UnittestRunner, CondaPythonManager


def main() -> None:
    publish(
        name="quickpub",
        version="1.0.1",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["danielutils>=0.9.90"],
        min_python="3.8.0",
        config=AdditionalConfiguration(
            python_manager=CondaPythonManager(["base", "390", "380"]),
            runners=[
                MypyRunner(bound="<=15", configuration_path="./mypy.ini"),
                PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
                UnittestRunner(bound=">=0.8"),
            ]
        )
    )


if __name__ == '__main__':
    main()
