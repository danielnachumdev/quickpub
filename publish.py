from tqdm import tqdm

from quickpub import (
    main as entry_point,
    publish,
    MypyRunner,
    PylintRunner,
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
        version="4.1.1",
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
        global_quality_assurance_runners=[
            MypyRunner(bound="<=20"),
            PylintRunner(bound=">=0.8"),
            PytestRunner(bound=">=0.95"),
        ],
        dependencies=["danielutils>=1.1.23", "requests", "fire", "twine"],
        min_python="3.8.0",
        scripts={"quickpub": entry_point},
        pbar=tqdm(desc="QA task", leave=False),  # type: ignore
        demo=False,
    )


if __name__ == "__main__":
    main()
