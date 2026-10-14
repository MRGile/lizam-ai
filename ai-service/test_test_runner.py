import os
import unittest

from app.tools.test_runner import LaravelTestRunner


class TestLaravelTestRunner(unittest.TestCase):
    def test_laravel_backend_path(self):
        backend_path = os.path.abspath(
            r"..\backend"
        )

        runner = LaravelTestRunner(backend_path)

        self.assertTrue(
            (runner.backend / "artisan").is_file()
        )

    def test_runs_laravel_tests(self):
        backend_path = os.path.abspath(
            r"..\backend"
        )

        runner = LaravelTestRunner(backend_path)
        result = runner.run()

        print("\nHasil Laravel Test Runner:")
        print(result["output"])

        self.assertTrue(result["tests_run"])
        self.assertIn(
            result["status"],
            {"passed", "failed", "timeout"},
        )

        if result["status"] == "passed":
            self.assertEqual(result["exit_code"], 0)
        elif result["status"] == "failed":
            self.assertNotEqual(result["exit_code"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
