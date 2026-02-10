import unittest
import os

class TestLab02Structure(unittest.TestCase):
    def test_files_exist(self):
        base_path = "labs/eigrp/lab-02-path-selection"
        self.assertTrue(os.path.exists(os.path.join(base_path, "challenges.md")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/fault_injector.py")))

    def test_injector_syntax(self):
        script_path = "labs/eigrp/lab-02-path-selection/scripts/fault_injector.py"
        with open(script_path, "r") as f:
            source = f.read()
            compile(source, script_path, "exec")

if __name__ == "__main__":
    unittest.main()
