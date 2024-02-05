import os
import tempfile
import unittest
from unittest.mock import Mock, patch

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
            # once for file, once for line, once for blank line
            self.assertEqual(1, mock_print.call_count)
            m = f'{f.name}:\n  1: Has pattern "[CX]PG\\d+": {contents.strip()}\n'
            mock_print.assert_called_once_with(m)

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
            # once for file, once for line, once for blank line
            self.assertEqual(1, mock_print.call_count)
            m = f'{f.name}:\n  2: Has pattern "[CX]PG\\d+": ID is: CPG123456\n'
            mock_print.assert_called_once_with(m)

    def test_fail_with_extra_pattern(self, mock_sys_exit: Mock, mock_print: Mock):
        # create temporary file with contents
        contents = """Test file with ABC ID on second line\nID is: ABC123456\n"""

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(contents)
            f.seek(0)
            cpg_id_checker_main(['--extra-pattern', 'ABC\\d+', f.name])
            # check that sys.exit was called with 1
            mock_sys_exit.assert_called_once_with(1)
            # once for file, once for line, once for blank line
            self.assertEqual(1, mock_print.call_count)
            m = f'{f.name}:\n  2: Has pattern "ABC\\d+": ID is: ABC123456\n'
            mock_print.assert_called_once_with(m)

    def test_ignore_image_extension(self, mock_sys_exit: Mock, mock_print: Mock):
        # create temporary file with contents

        with tempfile.NamedTemporaryFile(suffix="file.png", mode='w+') as f:
            f.write("this will get ignored anyway")
            f.seek(0)
            cpg_id_checker_main([f.name])
            # check that sys.exit was called with 1
            mock_sys_exit.assert_called_once_with(0)
            # once for file, once for line, once for blank line
            self.assertEqual(0, mock_print.call_count)

    def test_ignore_binary_file(self, mock_sys_exit: Mock, mock_print: Mock):
        # use a tiny 10x10 png image (binary) presented as a text file
        p = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'resources',
            'image.png.txt',
        )
        cpg_id_checker_main([p])
        # check that sys.exit was called with 1
        mock_sys_exit.assert_called_once_with(0)
        # once for file, once for line, once for blank line
        self.assertEqual(0, mock_print.call_count)

    def test_ignore_regex_patterned_file(self, mock_sys_exit: Mock, mock_print: Mock):
        # use a tiny 10x10 png image (binary) presented as a text file
        with tempfile.NamedTemporaryFile(suffix="file.txt", mode='w+') as f:
            f.write("this will get ignored anyway")
            f.seek(0)
            cpg_id_checker_main(['--ignore-filename-format', r'\.txt$', f.name])
            # check that sys.exit was called with 1
            mock_sys_exit.assert_called_once_with(0)
            # once for file, once for line, once for blank line
            self.assertEqual(0, mock_print.call_count)
