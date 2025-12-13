import unittest

from quickpub.classifiers import (
    Classifier,
    DevelopmentStatusClassifier,
    IntendedAudienceClassifier,
    ProgrammingLanguageClassifier,
    OperatingSystemClassifier,
)


class TestClassifierSplitName(unittest.TestCase):
    def test_single_word(self) -> None:
        result = Classifier._split_name("Alpha")
        self.assertEqual(result, "")

    def test_camel_case_two_words(self) -> None:
        result = Classifier._split_name("DevelopmentStatus")
        self.assertEqual(result, "Development")

    def test_camel_case_three_words(self) -> None:
        result = Classifier._split_name("IntendedAudienceClassifier")
        self.assertEqual(result, "Intended Audience")

    def test_camel_case_four_words(self) -> None:
        result = Classifier._split_name("ProgrammingLanguageClassifier")
        self.assertEqual(result, "Programming Language")

    def test_all_uppercase(self) -> None:
        result = Classifier._split_name("ABC")
        self.assertEqual(result, "A B")

    def test_mixed_case(self) -> None:
        result = Classifier._split_name("OperatingSystemClassifier")
        self.assertEqual(result, "Operating System")


class TestClassifierStr(unittest.TestCase):
    def test_development_status_classifier_str(self) -> None:
        classifier = DevelopmentStatusClassifier.Alpha
        result = str(classifier)
        self.assertIn("Development Status", result)
        self.assertIn("3 - Alpha", result)

    def test_intended_audience_classifier_str(self) -> None:
        classifier = IntendedAudienceClassifier.Developers
        result = str(classifier)
        self.assertIn("Intended Audience", result)
        self.assertIn("Developers", result)

    def test_programming_language_classifier_str(self) -> None:
        classifier = ProgrammingLanguageClassifier.Python3
        result = str(classifier)
        self.assertIn("Programming Language", result)
        self.assertIn("Python :: 3", result)

    def test_operating_system_classifier_str(self) -> None:
        classifier = OperatingSystemClassifier.MicrosoftWindows
        result = str(classifier)
        self.assertIn("Operating System", result)
        self.assertIn("Microsoft :: Windows", result)


class TestDevelopmentStatusClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(DevelopmentStatusClassifier.Planning.value, 1)
        self.assertEqual(DevelopmentStatusClassifier.PreAlpha.value, 2)
        self.assertEqual(DevelopmentStatusClassifier.Alpha.value, 3)
        self.assertEqual(DevelopmentStatusClassifier.Beta.value, 4)
        self.assertEqual(DevelopmentStatusClassifier.Production.value, 5)
        self.assertEqual(DevelopmentStatusClassifier.Stable.value, 5)
        self.assertEqual(DevelopmentStatusClassifier.Mature.value, 6)
        self.assertEqual(DevelopmentStatusClassifier.Inactive.value, 7)

    def test_custom_str_format(self) -> None:
        classifier = DevelopmentStatusClassifier.Alpha
        result = classifier._str()
        self.assertEqual(result, "3 - Alpha")

    def test_all_classifiers_have_custom_str(self) -> None:
        for classifier in DevelopmentStatusClassifier:
            result = classifier._str()
            self.assertIn(str(classifier.value), result)
            self.assertIn(classifier.name, result)


class TestIntendedAudienceClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(
            IntendedAudienceClassifier.CustomerService.value, "CustomerService"
        )
        self.assertEqual(IntendedAudienceClassifier.Developers.value, "Developers")

    def test_str_representation(self) -> None:
        classifier = IntendedAudienceClassifier.Developers
        result = str(classifier)
        self.assertIn("Intended Audience", result)
        self.assertIn("Developers", result)


class TestProgrammingLanguageClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(ProgrammingLanguageClassifier.Python3.value, "Python :: 3")

    def test_str_representation(self) -> None:
        classifier = ProgrammingLanguageClassifier.Python3
        result = str(classifier)
        self.assertIn("Programming Language", result)
        self.assertIn("Python :: 3", result)


class TestOperatingSystemClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(
            OperatingSystemClassifier.MicrosoftWindows.value, "Microsoft :: Windows"
        )

    def test_str_representation(self) -> None:
        classifier = OperatingSystemClassifier.MicrosoftWindows
        result = str(classifier)
        self.assertIn("Operating System", result)
        self.assertIn("Microsoft :: Windows", result)


if __name__ == "__main__":
    unittest.main()
