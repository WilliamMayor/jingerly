import os
import unittest
import shutil

import jingerly


class TestAll(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAll, self).__init__(*args, **kwargs)
        self.addCleanup(self.cleanUp)

    def setUp(self):
        jingerly.render(
            'tests/template/all',
            'tests/actual/all',
            name='actual',
            known='this is known')

    def cleanUp(self):
        shutil.rmtree('tests/actual/all')

    def assertFilesEqual(self, expected, actual):
        with open(expected, 'rb') as fd:
            expected_contents = fd.read()
        try:
            with open(actual, 'rb') as fd:
                actual_contents = fd.read()
            self.assertEqual(
                actual_contents, expected_contents)
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

    def test_known_variables(self):
        self.assertFilesEqual(
            'tests/expected/all/known_variables.txt',
            'tests/actual/all/known_variables.txt')

    def test_unknown_variables(self):
        self.assertFilesEqual(
            'tests/expected/all/unknown_variables.txt',
            'tests/actual/all/unknown_variables.txt')
