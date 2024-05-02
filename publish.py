from quickpub import publish, AdditionalConfiguration, MypyRunner, PylintRunner, UnittestRunner, CondaPythonManager
from danielutils import ProgressBarPool, AsciiProgressBar,bprint
import time


def main() -> None:
    # n = 5
    # pool = ProgressBarPool(
    #     AsciiProgressBar,
    #     3,
    #     individual_options=[
    #         dict(iterable=range(n), desc="deco"),
    #         dict(iterable=range(n), desc="wrapper"),
    #         dict(iterable=range(n), desc="inner")
    #     ]
    # )
    # for _ in pool[0]:
    #     for _ in pool[1]:
    #         for _ in pool[2]:
    #             time.sleep(0.1)
    #             pool[2].write("2")
    #             pool[1].write("foo")
    #     pool.write("bar")
    publish(
        name="quickpub",
        version="0.9.0",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["twine", "danielutils"],
        min_python="3.8.0",
        config=AdditionalConfiguration(
            python_manager=CondaPythonManager(["base", "390", "380"]),
            runners=[
                MypyRunner(bound="<15", configuration_path="./mypy.ini"),
                PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
                UnittestRunner(bound=">=0.8"),
            ]
        )
    )


if __name__ == '__main__':
    main()
