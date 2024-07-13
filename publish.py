from quickpub import publish, MypyRunner, PylintRunner, UnittestRunner, CondaPythonManager, \
    PypircUploadStrategy, SetuptoolsBuildStrategy, GitUploadStrategy


def main() -> None:
    publish(
        name="quickpub",
        version="1.0.1",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        python_version_manager_strategy=CondaPythonManager(["base", "390", "380"]),
        quality_assurance_strategies=[
            MypyRunner(bound="<=15", configuration_path="./mypy.ini"),
            PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
            UnittestRunner(bound=">=0.8"),
        ],
        build_strategies=[SetuptoolsBuildStrategy()],
        upload_strategies=[PypircUploadStrategy(), GitUploadStrategy()],
        dependencies=["danielutils>=0.9.90"],
        min_python="3.8.0",
        demo=True
    )


if __name__ == '__main__':
    main()
