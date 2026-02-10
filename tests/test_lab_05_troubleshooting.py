import unittest
import os

class TestLab05Structure(unittest.TestCase):
    def test_files_exist(self):
        base_path = "labs/eigrp/lab-05-authentication-advanced"
        self.assertTrue(os.path.exists(os.path.join(base_path, "challenges.md")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/refresh_lab.py")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/fault_inject_1.py")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/fault_inject_2.py")))
        self.assertTrue(os.path.exists(os.path.join(base_path, "scripts/fault_inject_3.py")))

    def test_scripts_syntax(self):
        scripts = [
            "labs/eigrp/lab-05-authentication-advanced/scripts/refresh_lab.py",
            "labs/eigrp/lab-05-authentication-advanced/scripts/fault_inject_1.py",
            "labs/eigrp/lab-05-authentication-advanced/scripts/fault_inject_2.py",
            "labs/eigrp/lab-05-authentication-advanced/scripts/fault_inject_3.py"
        ]
        for script_path in scripts:
            with open(script_path, "r") as f:
                source = f.read()
                compile(source, script_path, "exec")

if __name__ == "__main__":
    unittest.main()
