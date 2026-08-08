import unittest

from quickpub.classifiers import (
    Classifier,
    DevelopmentStatusClassifier,
    EnvironmentClassifier,
    IntendedAudienceClassifier,
    LicenseClassifier,
    OperatingSystemClassifier,
    ProgrammingLanguageClassifier,
    TopicClassifier,
    TypingClassifier,
    default_publish_classifiers,
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
        result = str(DevelopmentStatusClassifier.Alpha)
        self.assertEqual(result, "Development Status :: 3 - Alpha")

    def test_pre_alpha_uses_official_label(self) -> None:
        result = str(DevelopmentStatusClassifier.PreAlpha)
        self.assertEqual(result, "Development Status :: 2 - Pre-Alpha")

    def test_production_and_stable_use_official_label(self) -> None:
        self.assertEqual(
            str(DevelopmentStatusClassifier.Production),
            "Development Status :: 5 - Production/Stable",
        )
        self.assertEqual(
            str(DevelopmentStatusClassifier.Stable),
            "Development Status :: 5 - Production/Stable",
        )

    def test_intended_audience_classifier_str(self) -> None:
        result = str(IntendedAudienceClassifier.Developers)
        self.assertEqual(result, "Intended Audience :: Developers")

    def test_customer_service_has_space(self) -> None:
        result = str(IntendedAudienceClassifier.CustomerService)
        self.assertEqual(result, "Intended Audience :: Customer Service")

    def test_programming_language_classifier_str(self) -> None:
        result = str(ProgrammingLanguageClassifier.Python3)
        self.assertEqual(result, "Programming Language :: Python :: 3")

    def test_python_3_only(self) -> None:
        result = str(ProgrammingLanguageClassifier.Python3Only)
        self.assertEqual(result, "Programming Language :: Python :: 3 :: Only")

    def test_operating_system_windows(self) -> None:
        result = str(OperatingSystemClassifier.MicrosoftWindows)
        self.assertEqual(result, "Operating System :: Microsoft :: Windows")

    def test_operating_system_independent(self) -> None:
        result = str(OperatingSystemClassifier.OSIndependent)
        self.assertEqual(result, "Operating System :: OS Independent")

    def test_license_mit(self) -> None:
        result = str(LicenseClassifier.MIT)
        self.assertEqual(result, "License :: OSI Approved :: MIT License")

    def test_topic_build_tools(self) -> None:
        result = str(TopicClassifier.BuildTools)
        self.assertEqual(result, "Topic :: Software Development :: Build Tools")

    def test_typing_typed(self) -> None:
        result = str(TypingClassifier.Typed)
        self.assertEqual(result, "Typing :: Typed")

    def test_environment_console(self) -> None:
        result = str(EnvironmentClassifier.Console)
        self.assertEqual(result, "Environment :: Console")


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

    def test_official_labels(self) -> None:
        expected = {
            DevelopmentStatusClassifier.Planning: "1 - Planning",
            DevelopmentStatusClassifier.PreAlpha: "2 - Pre-Alpha",
            DevelopmentStatusClassifier.Alpha: "3 - Alpha",
            DevelopmentStatusClassifier.Beta: "4 - Beta",
            DevelopmentStatusClassifier.Production: "5 - Production/Stable",
            DevelopmentStatusClassifier.Stable: "5 - Production/Stable",
            DevelopmentStatusClassifier.Mature: "6 - Mature",
            DevelopmentStatusClassifier.Inactive: "7 - Inactive",
        }
        for classifier, label in expected.items():
            self.assertEqual(classifier._str(), label)


class TestIntendedAudienceClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(
            IntendedAudienceClassifier.CustomerService.value, "Customer Service"
        )
        self.assertEqual(IntendedAudienceClassifier.Developers.value, "Developers")

    def test_str_representation(self) -> None:
        result = str(IntendedAudienceClassifier.Developers)
        self.assertEqual(result, "Intended Audience :: Developers")


class TestProgrammingLanguageClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(ProgrammingLanguageClassifier.Python3.value, "Python :: 3")
        self.assertEqual(ProgrammingLanguageClassifier.Python38.value, "Python :: 3.8")
        self.assertEqual(ProgrammingLanguageClassifier.Python313.value, "Python :: 3.13")

    def test_str_representation(self) -> None:
        result = str(ProgrammingLanguageClassifier.Python3)
        self.assertEqual(result, "Programming Language :: Python :: 3")


class TestOperatingSystemClassifier(unittest.TestCase):
    def test_all_enum_values(self) -> None:
        self.assertEqual(
            OperatingSystemClassifier.MicrosoftWindows.value, "Microsoft :: Windows"
        )
        self.assertEqual(OperatingSystemClassifier.OSIndependent.value, "OS Independent")

    def test_str_representation(self) -> None:
        result = str(OperatingSystemClassifier.MicrosoftWindows)
        self.assertEqual(result, "Operating System :: Microsoft :: Windows")


class TestDefaultPublishClassifiers(unittest.TestCase):
    def test_defaults_are_os_independent_not_windows(self) -> None:
        classifiers = default_publish_classifiers()
        rendered = [str(classifier) for classifier in classifiers]
        self.assertIn("Operating System :: OS Independent", rendered)
        self.assertNotIn("Operating System :: Microsoft :: Windows", rendered)
        self.assertIn("Development Status :: 3 - Alpha", rendered)
        self.assertIn("Intended Audience :: Developers", rendered)
        self.assertIn("Programming Language :: Python :: 3", rendered)


if __name__ == "__main__":
    unittest.main()
