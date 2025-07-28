import unittest
from functions.get_file_content import get_file_content
import os

class TestGetFileContent(unittest.TestCase):
    def setUp(self):
        # Setup: create test files
        os.makedirs("calculator/pkg", exist_ok=True)
        with open("calculator/main.py", "w") as f:
            f.write("print('main')")
        with open("calculator/pkg/calculator.py", "w") as f:
            f.write("def add(a, b): return a + b")

    def tearDown(self):
        # Cleanup: remove test files
        os.remove("calculator/main.py")
        os.remove("calculator/pkg/calculator.py")
        os.rmdir("calculator/pkg")
        os.rmdir("calculator")

    def test_main_py(self):
        content = get_file_content("calculator", "main.py")
        self.assertIn("print('main')", content)

    def test_pkg_calculator_py(self):
        content = get_file_content("calculator", "pkg/calculator.py")
        self.assertIn("def add(a, b):", content)

    def test_invalid_path(self):
        content = get_file_content("calculator", "/bin/cat")
        self.assertTrue(content is None or content == "")

    def test_nonexistent_file(self):
        content = get_file_content("calculator", "does_not_exist.py")
        self.assertTrue(content is None or content == "")

if __name__ == "__main__":
    unittest.main()