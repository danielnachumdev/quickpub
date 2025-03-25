from typing import AsyncIterator, Tuple, TypeVar

from danielutils import AsyncWorkerPool, AsyncAutoCWDTestCase

from quickpub import CondaPythonProvider

T = TypeVar("T")


async def async_enumerate(iterable: AsyncIterator[T], start: int = 0) -> AsyncIterator[Tuple[int, T]]:
    index = start
    async for item in iterable:
        yield index, item
        index += 1


class TestCondaPythonProvider(AsyncAutoCWDTestCase):
    async def test_all_envs_should_succeed(self):
        envs = await CondaPythonProvider.get_available_envs()
        provider = CondaPythonProvider(list(envs))
        pool = AsyncWorkerPool("TestCondaPythonProvider", num_workers=5)

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

        async for i, tup in async_enumerate(provider):
            env_name, executor = tup
            await pool.submit(wrapper, args=[env_name, executor])

        await pool.start()
        await pool.join()
