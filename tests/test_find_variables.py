import unittest

import jingerly


class TestFindVariables(unittest.TestCase):

    def test_find_variables(self):
        variables = jingerly.find_variables('tests/template/single_file')
        self.assertEqual(set(['name', 'one', 'two']), set(variables))
