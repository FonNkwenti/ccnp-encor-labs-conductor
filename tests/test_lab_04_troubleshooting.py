import unittest
import os

class TestLab04Structure(unittest.TestCase):
    def test_files_exist(self):
        base_path = "labs/eigrp/lab-04-stub-wan-opt"
        self.assertTrue(os.path.exists(os.path.join(base_path, "challenges.md")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/fault_injector.py")))

    def test_injector_syntax(self):
        script_path = "labs/eigrp/lab-04-stub-wan-opt/scripts/fault_injector.py"
        if os.path.exists(script_path):
            with open(script_path, "r") as f:
                source = f.read()
                compile(source, script_path, "exec")
        else:
            self.fail("fault_injector.py does not exist yet")

if __name__ == "__main__":
    unittest.main()
