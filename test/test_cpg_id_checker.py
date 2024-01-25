import tempfile
import unittest
from unittest.mock import Mock, call, patch

from pre_commit_hooks.cpg_id_checker import main as cpg_id_checker_main


# we'll patch the system print call to check what is printed
@patch('pre_commit_hooks.cpg_id_checker.print')
# catch sys.exit call too
@patch('pre_commit_hooks.cpg_id_checker.sys.exit')
class CPGIDChecker(unittest.TestCase):
    def test_pass(self, mock_sys_exit: Mock, mock_print: Mock):
        # create temporary file with contents
        contents = """
        This is a test file with no CPG IDs
        CPG 1
        CPG\\d
        CPGabc
        """

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(contents)
            cpg_id_checker_main([f.name])
            # check that sys.exit was called with 0
            mock_sys_exit.assert_called_once_with(0)
            mock_print.assert_not_called()

    def test_fail_with_cpg_id(self, mock_sys_exit: Mock, mock_print: Mock):
        # create temporary file with contents
        contents = """This is a test file with CPG123456\n"""

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(contents)
            f.seek(0)
            cpg_id_checker_main([f.name])
            # check that sys.exit was called with 1
            mock_sys_exit.assert_called_once_with(1)
            self.assertEqual(2, mock_print.call_count)
            mock_print.assert_has_calls(
                [
                    call(f'{f.name}:'),
                    call(f'  1: Has pattern "[CX]PG\\d+": {contents.strip()}'),
                ],
            )

    def test_fail_with_cpg_id_on_second_line(
        self,
        mock_sys_exit: Mock,
        mock_print: Mock,
    ):
        # create temporary file with contents
        contents = """Test file with CPG ID on second line\nID is: CPG123456\n"""

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(contents)
            f.seek(0)
            cpg_id_checker_main([f.name])
            # check that sys.exit was called with 1
            mock_sys_exit.assert_called_once_with(1)
            self.assertEqual(2, mock_print.call_count)
            mock_print.assert_has_calls(
                [
                    call(f'{f.name}:'),
                    call('  2: Has pattern "[CX]PG\\d+": ID is: CPG123456'),
                ],
            )

    def test_fail_with_extra_pattern(self, mock_sys_exit: Mock, mock_print: Mock):
        # create temporary file with contents
        contents = """Test file with ABC ID on second line\nID is: ABC123456\n"""

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(contents)
            f.seek(0)
            cpg_id_checker_main(['--extra-pattern', 'ABC\\d+', f.name])
            # check that sys.exit was called with 1
            mock_sys_exit.assert_called_once_with(1)
            self.assertEqual(2, mock_print.call_count)
            mock_print.assert_has_calls(
                [
                    call(f'{f.name}:'),
                    call('  2: Has pattern "ABC\\d+": ID is: ABC123456'),
                ],
            )
