import asyncio
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Coroutine, Optional

from quickpub import CondaPythonProvider


def run_async(coroutine: Coroutine) -> Optional[Exception]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coroutine)
    except Exception as e:
        return e
    finally:
        loop.close()
    return None


class TestCondaPythonProvider(unittest.IsolatedAsyncioTestCase):
    async def test_all_envs_should_succeed(self):
        envs = await CondaPythonProvider.get_available_envs()
        provider = CondaPythonProvider(list(envs))
        futures = []
        with ThreadPoolExecutor() as pool:
            for i, tup in enumerate(provider):
                async def wrapper(env_name, executor) -> None:
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

                env_name, executor = tup
                coro = wrapper(env_name, executor)
                futures.append(pool.submit(run_async, coro))
            for future in futures:
                exception = future.result()
                if exception:
                    raise exception
