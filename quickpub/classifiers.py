from abc import ABC, abstractmethod
from enum import Enum


class Classifier(Enum):
    """
    A base enum class for all classifiers.
    """

    def _str(self) -> str:
        return str(self.value)

    @staticmethod
    def _split_name(name: str) -> str:
        words = []
        current_word = ''

        for char in name:
            # Check if the character is uppercase
            if char.isupper():
                # If current_word is not empty, add it to words list
                if current_word:
                    words.append(current_word)
                # Start a new word with the uppercase character
                current_word = char
            else:
                # Add lowercase character to current_word
                current_word += char

        # Add the last word to the list
        if current_word:
            words.append(current_word)

        return " ".join(words[:-1])

    def __str__(self) -> str:
        name = Classifier._split_name(self.__class__.__qualname__)
        value = self._str()
        return f"{name} :: {value}"


class DevelopmentStatusClassifier(Classifier):
    """
    An enum class for specifying the development state of the package
    """
    # https://pypi.org/classifiers/
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
    """
    An enum class for specifying the intended audience
    """
    CustomerService = "CustomerService"
    Developers = "Developers"


class ProgrammingLanguageClassifier(Classifier):
    """
    An enum class for specifying the target language level
    """
    Python3 = "Python :: 3"


class OperatingSystemClassifier(Classifier):
    """
    An enum class for specifying the target operating system
    """
    MicrosoftWindows = "Microsoft :: Windows"


__all__ = [
    "Classifier",
    "DevelopmentStatusClassifier",
    "IntendedAudienceClassifier",
    "ProgrammingLanguageClassifier",
    "OperatingSystemClassifier"
]
