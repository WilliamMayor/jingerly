import os
import unittest
import shutil

import jingerly


class TestAll(unittest.TestCase):

    def setUp(self):
        jingerly.render(
            'tests/template/all',
            'tests/actual/all',
            name='actual',
            known='this is known')

    def tearDown(self):
        shutil.rmtree('tests/actual/all')

    def assertFilesEqual(self, expected, actual):
        with open(expected, 'rb') as fd:
            expected_contents = fd.read()
        try:
            with open(actual, 'rb') as fd:
                actual_contents = fd.read()
            self.assertEqual(
                actual_contents, expected_contents, 'File contants differed')
        except IOError:
            self.fail('File not created: %s' % actual)

    def assertFoldersEqual(self, expected, actual):
        expected_name = os.path.basename(expected)
        actual_name = os.path.basename(actual)
        self.assertEqual(
            actual_name, expected_name, 'Folder names differed')

    def test_untouched(self):
        self.assertFilesEqual(
            'tests/expected/all/untouched.txt',
            'tests/actual/all/untouched.txt')
