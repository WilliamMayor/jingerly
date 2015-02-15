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
            known='this is known',
            _ignore=['.DS_Store', '.git', 'jingerly.envc'])

    def cleanUp(self):
        try:
            shutil.rmtree('tests/actual/all')
        except OSError:
            pass

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

    def test_rename_file(self):
        self.assertFilesEqual(
            'tests/expected/all/file_with_actual.txt',
            'tests/actual/all/file_with_actual.txt')

    def test_rename_folder(self):
        self.assertFilesEqual(
            'tests/expected/all/folder_with_actual/expected.txt',
            'tests/actual/all/folder_with_actual/expected.txt')

    def test_copy_filter(self):
        self.assertFilesEqual(
            'tests/expected/all/copy_file.txt',
            'tests/actual/all/copy_file.txt')

    def test_download_filter(self):
        self.assertFilesEqual(
            'tests/expected/all/download_file.txt',
            'tests/actual/all/download_file.txt')

    def test_pre_script(self):
        self.assertFilesEqual(
            'tests/expected/all/made_in_pre',
            'tests/actual/all/made_in_pre')

    def test_post_script(self):
        self.assertFilesEqual(
            'tests/expected/all/made_in_post',
            'tests/actual/all/made_in_post')

    def test_every_file(self):
        ignore = ['jingerly.envc']
        for root, dirs, files in os.walk('tests/expected/all'):
            for f in files:
                if f in ignore:
                    continue
                self.assertFilesEqual(
                    os.path.join(root, f),
                    os.path.join(
                        root.replace('tests/expected/all', 'tests/actual/all'),
                        f))
        for root, dirs, files in os.walk('tests/actual/all'):
            for f in files:
                if f in ignore:
                    continue
                self.assertTrue(os.path.isfile(
                    os.path.join(
                        root.replace('tests/actual/all', 'tests/expected/all'),
                        f)))
