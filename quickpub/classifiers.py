import logging
from enum import Enum
from typing import List

logger = logging.getLogger(__name__)

_DEVELOPMENT_STATUS_LABELS = {
    1: "Planning",
    2: "Pre-Alpha",
    3: "Alpha",
    4: "Beta",
    5: "Production/Stable",
    6: "Mature",
    7: "Inactive",
}


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
    Planning = 1
    PreAlpha = 2
    Alpha = 3
    Beta = 4
    Production = 5
    Stable = 5
    Mature = 6
    Inactive = 7

    def _str(self) -> str:
        return f"{self.value} - {_DEVELOPMENT_STATUS_LABELS[self.value]}"


class IntendedAudienceClassifier(Classifier):
    CustomerService = "Customer Service"
    Developers = "Developers"
    Education = "Education"
    EndUsersDesktop = "End Users/Desktop"
    InformationTechnology = "Information Technology"
    ScienceResearch = "Science/Research"
    SystemAdministrators = "System Administrators"


class ProgrammingLanguageClassifier(Classifier):
    Python = "Python"
    Python3 = "Python :: 3"
    Python3Only = "Python :: 3 :: Only"
    Python38 = "Python :: 3.8"
    Python39 = "Python :: 3.9"
    Python310 = "Python :: 3.10"
    Python311 = "Python :: 3.11"
    Python312 = "Python :: 3.12"
    Python313 = "Python :: 3.13"


class OperatingSystemClassifier(Classifier):
    OSIndependent = "OS Independent"
    MicrosoftWindows = "Microsoft :: Windows"
    POSIX = "POSIX"
    Linux = "POSIX :: Linux"
    MacOS = "MacOS"
    Unix = "Unix"


class LicenseClassifier(Classifier):
    MIT = "OSI Approved :: MIT License"
    Apache2 = "OSI Approved :: Apache Software License"
    BSD = "OSI Approved :: BSD License"
    GPLv3 = "OSI Approved :: GNU General Public License v3 (GPLv3)"


class TopicClassifier(Classifier):
    SoftwareDevelopment = "Software Development"
    BuildTools = "Software Development :: Build Tools"
    Libraries = "Software Development :: Libraries"
    PythonModules = "Software Development :: Libraries :: Python Modules"
    QualityAssurance = "Software Development :: Quality Assurance"
    Testing = "Software Development :: Testing"


class TypingClassifier(Classifier):
    Typed = "Typed"


class EnvironmentClassifier(Classifier):
    Console = "Console"


def default_publish_classifiers() -> List[Classifier]:
    return [
        DevelopmentStatusClassifier.Alpha,
        IntendedAudienceClassifier.Developers,
        ProgrammingLanguageClassifier.Python3,
        OperatingSystemClassifier.OSIndependent,
    ]


__all__ = [
    "Classifier",
    "DevelopmentStatusClassifier",
    "IntendedAudienceClassifier",
    "ProgrammingLanguageClassifier",
    "OperatingSystemClassifier",
    "LicenseClassifier",
    "TopicClassifier",
    "TypingClassifier",
    "EnvironmentClassifier",
    "default_publish_classifiers",
]
