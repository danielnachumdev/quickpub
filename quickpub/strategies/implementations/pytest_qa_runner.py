import re
from typing import List, Union, Optional

from danielutils import LayeredCommand

from quickpub import Bound
from ..quality_assurance_runner import QualityAssuranceRunner

class PytestRunner(QualityAssuranceRunner):
    """
    PytestRunner is a concrete implementation of QualityAssuranceRunner specifically for running
    pytest-based tests. It includes methods to build the pytest command, install pytest dependencies,
    and calculate the test score based on pytest results.

    Attributes:
        PYTEST_REGEX (re.Pattern): A regex pattern to parse pytest results for passed and failed tests.
    """

    PYTEST_REGEX: re.Pattern = re.compile(
        r"=+ (?:(?P<failed>\d+) failed,? )?(?:(?P<passed>\d+) passed )?in [\d\.]+s =+")

    def __init__(self, *, bound: Union[str, Bound] = ">=0.8", target: str = "./tests"):
        """
        Initializes the PytestRunner with a bound and target directory for tests.

        :param bound: The bound representing acceptable limits, either as a string or a Bound object.
                      Default is ">=0.8".
        :param target: The target directory containing the tests. Default is "./tests".
        """
        super().__init__(
            name="pytest",
            bound=bound,
            target=target
        )

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        """
        Builds the command to run pytest on the specified target.

        :param target: The target directory containing the tests.
        :param use_system_interpreter: Whether to use the system interpreter. Default is False.
        :return: The command to run pytest as a string.
        """
        if self.has_config:
            return "pytest"
        return f"pytest {self.target}"

    def _install_dependencies(self, base: LayeredCommand) -> None:
        """
        Installs pytest and its dependencies.

        :param base: The base LayeredCommand object for executing commands.
        """
        with base:
            base("pip install pytest")

    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        """
        Calculates the test score based on the pytest command output.

        :param ret: The return code of the pytest command.
        :param command_output: The output of the pytest command as a list of strings.
        :param verbose: Whether to output verbose logs. Default is False.
        :return: The calculated test score as a float.
        """
        if len(command_output) == 0:
            return 0
        rating_line = command_output[-1]
        if "no tests ran" in rating_line:
            return 1.0
        if not (m := self.PYTEST_REGEX.match(rating_line)):
            raise SystemExit(1)

        dct = m.groupdict()
        failed = int(dct["failed"] or "0")
        passed = int(dct["passed"] or "0")
        assert failed >= 0
        assert passed >= 0
        if failed + passed == 0:
            return 1.0
        return passed / (passed + failed)
