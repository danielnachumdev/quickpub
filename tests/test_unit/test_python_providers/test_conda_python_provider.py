import unittest
from quickpub import CondaPythonProvider


class TestCondaPythonProvider(unittest.TestCase):
    def test_all_envs_should_succeed(self):
        envs = CondaPythonProvider.get_available_envs()
        provider = CondaPythonProvider(list(envs))
        for env_name, executor in provider:
            expected_index: int = 0
            with executor:
                code, stdout, stderr = executor.execute("conda info")
            self.assertEqual(0, code)
            self.assertTrue(len(stdout) > 0, "stdout should not be empty")
            self.assertTrue(len(stderr) == 0, "stderr should be empty")
            if stdout[0] == '\x1b[0m\n':
                expected_index: int = 1

            indicator_line = stdout[expected_index].strip()
            current_env = indicator_line.split(' ')[-1]
            self.assertIn(current_env, envs)
