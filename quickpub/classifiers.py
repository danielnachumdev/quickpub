import logging
from enum import Enum

logger = logging.getLogger(__name__)


class Classifier(Enum):

    def _str(self) -> str:
        return str(self.value)

    @staticmethod
    def _split_name(name: str) -> str:
        words = []
        current_word = ""

        for char in name:
            if char.isupper():
                if current_word:
                    words.append(current_word)
                current_word = char
            else:
                current_word += char

        if current_word:
            words.append(current_word)

        return " ".join(words[:-1])

    def __str__(self) -> str:
        name = Classifier._split_name(self.__class__.__qualname__)
        value = self._str()
        result = f"{name} :: {value}"
        logger.debug("Classifier string representation: %s", result)
        return result


class DevelopmentStatusClassifier(Classifier):
    """Classifier for package development status. Use values like Alpha, Beta, Production, etc."""

    Planning = 1
    PreAlpha = 2
    Alpha = 3
    Beta = 4
    Production = 5
    Stable = 5
    Mature = 6
    Inactive = 7

    def _str(self) -> str:
        return f"{self.value} - {self.name}"


class IntendedAudienceClassifier(Classifier):
    """Classifier for intended audience of the package."""

    CustomerService = "CustomerService"
    Developers = "Developers"


class ProgrammingLanguageClassifier(Classifier):
    """Classifier for programming languages supported by the package."""

    Python3 = "Python :: 3"


class OperatingSystemClassifier(Classifier):
    """Classifier for operating systems supported by the package."""

    MicrosoftWindows = "Microsoft :: Windows"


__all__ = [
    "Classifier",
    "DevelopmentStatusClassifier",
    "IntendedAudienceClassifier",
    "ProgrammingLanguageClassifier",
    "OperatingSystemClassifier",
]
