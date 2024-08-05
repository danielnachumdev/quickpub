from quickpub import publish, MypyRunner, PylintRunner, UnittestRunner, CondaPythonProvider, \
    PypircUploadTarget, SetuptoolsBuildSchema, GithubUploadTarget, PypircEnforcer, ReadmeEnforcer, LicenseEnforcer, \
    PypiRemoteVersionEnforcer, LocalVersionEnforcer


def main() -> None:
    publish(
        name="quickpub",
        version="2.0.1",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        enforcers=[
            PypircEnforcer(), ReadmeEnforcer(), LicenseEnforcer(),
            LocalVersionEnforcer(), PypiRemoteVersionEnforcer()
        ],
        build_schemas=[SetuptoolsBuildSchema()],
        upload_targets=[PypircUploadTarget(), GithubUploadTarget()],
        python_interpreter_provider=CondaPythonProvider(["base", "390", "380"]),
        global_quality_assurance_runners=[
            MypyRunner(bound="<=20", configuration_path="./mypy.ini"),
            PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
            UnittestRunner(bound=">=0.5"),
        ],
        dependencies=["danielutils>=0.9.94", "requests"],
        min_python="3.8.0",
    )


if __name__ == '__main__':
    main()
