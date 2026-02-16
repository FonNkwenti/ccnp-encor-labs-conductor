import unittest
from unittest.mock import patch, MagicMock, call
from labs.common.tools.fault_utils import FaultInjector

class TestFaultInjector(unittest.TestCase):
    def setUp(self):
        self.injector = FaultInjector(host="127.0.0.1")

    @patch('labs.common.tools.fault_utils.ConnectHandler')
    def test_execute_commands_success(self, mock_connect_handler):
        mock_conn = MagicMock()
        mock_connect_handler.return_value = mock_conn

        commands = ["interface Gi0/1", "shutdown"]
        result = self.injector.execute_commands(5001, commands, "Test Fault")

        self.assertTrue(result)
        mock_conn.send_config_set.assert_called_once_with(commands)
        mock_conn.disconnect.assert_called_once()

    @patch('labs.common.tools.fault_utils.ConnectHandler')
    def test_execute_commands_failure(self, mock_connect_handler):
        mock_connect_handler.side_effect = Exception("Connection refused")

        result = self.injector.execute_commands(5001, ["no int Gi0/1"], "Fail Test")

        self.assertFalse(result)

    @patch('labs.common.tools.fault_utils.ConnectHandler')
    def test_device_params(self, mock_connect_handler):
        mock_conn = MagicMock()
        mock_connect_handler.return_value = mock_conn

        self.injector.execute_commands(5001, ["show ip route"])

        mock_connect_handler.assert_called_once()
        device = mock_connect_handler.call_args[1] if mock_connect_handler.call_args[1] else mock_connect_handler.call_args[0][0]
        # ConnectHandler is called with **device, so args appear as kwargs
        kwargs = mock_connect_handler.call_args[1]
        self.assertEqual(kwargs["device_type"], "cisco_ios_telnet")
        self.assertEqual(kwargs["host"], "127.0.0.1")
        self.assertEqual(kwargs["port"], 5001)

if __name__ == '__main__':
    unittest.main()
