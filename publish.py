from tqdm import tqdm

from quickpub import (
    main as entry_point,
    publish,
    MypyRunner,
    PylintRunner,
    CondaPythonProvider,
    PypircUploadTarget,
    SetuptoolsBuildSchema,
    GithubUploadTarget,
    PypircEnforcer,
    ReadmeEnforcer,
    LicenseEnforcer,
    PypiRemoteVersionEnforcer,
    LocalVersionEnforcer,
    PytestRunner,
)


def main() -> None:
    publish(
        name="quickpub",
        version="3.1.0",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A local CI/CD simulation tool that runs quality checks, tests, and validations locally before publishing Python packages, ensuring higher build pass rates and faster feedback loops",
        homepage="https://github.com/danielnachumdev/quickpub",
        enforcers=[
            PypircEnforcer(),
            ReadmeEnforcer(),
            LicenseEnforcer(),
            LocalVersionEnforcer(),
            PypiRemoteVersionEnforcer(),
        ],
        build_schemas=[SetuptoolsBuildSchema()],
        upload_targets=[PypircUploadTarget(), GithubUploadTarget()],
        python_interpreter_provider=CondaPythonProvider(["base", "390", "380"]),
        global_quality_assurance_runners=[
            MypyRunner(bound="<=20", configuration_path="./mypy.ini"),
            PylintRunner(bound=">=0.8", configuration_path="./.pylintrc"),
            PytestRunner(bound=">=0.95"),
        ],
        dependencies=["danielutils>=1.0.0", "requests", "fire"],
        min_python="3.8.0",
        scripts={"quickpub": entry_point},
        pbar=tqdm(desc="QA task", leave=False),  # type: ignore
        demo=True,
    )


if __name__ == "__main__":
    main()
