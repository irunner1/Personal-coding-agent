import unittest

from functions.run_python_file import run_python_file


class TestCalculator(unittest.TestCase):
    def test_main(self):
        result = run_python_file("calculator", "main.py")
        print(result)
        assert (
            result
            == """STDOUT: Calculator App\nUsage: python main.py "<expression>"\nExample: python main.py "3 + 5"\nSTDERR: """
        )

    def test_calculator_run(self):
        result = run_python_file("calculator", "main.py", ["3 + 5"])

        assert (
            result
            == """STDOUT: {
  "expression": "3 + 5",
  "result": 8
}
STDERR: """
        )

    def test_calc_tests(self):
        result = run_python_file("calculator", "tests.py")

        assert (
            result
            == """STDOUT: STDERR: .........
----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
"""
        )

    def test_calc_error(self):
        file_path = "../main.py"
        result = run_python_file("calculator", file_path)

        assert (
            result
            == f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        )

    def test_calc_none(self):
        filename = "nonexistent.p"
        result = run_python_file("calculator", filename)

        assert result == f'Error: "{filename}" does not exist or is not a regular file'

    def test_calc_text(self):
        file_path = "lorem.txt"
        result = run_python_file("calculator", file_path)

        assert result == f'Error: "{file_path}" is not a Python file'


if __name__ == "__main__":
    unittest.main()
