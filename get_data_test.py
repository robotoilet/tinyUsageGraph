import os
import unittest

import get_data

class TestGetData(unittest.TestCase):

    def setUp(self):
        """
        We're using test fixtures with some files to read, have a look at
        those.
        """
        self.rf = '^[CL]' # only accept filenames that start with 'C' or 'L'
        self.sort_func = lambda s: s[1:] # we want to sort on the timestamps

    def test_last_files_number_of_returned_files_1(self):
        filenames = get_data.last_files('fixtures', self.rf, 2, self.sort_func)
        self.assertEqual(len(filenames), 2)
        filenames = get_data.last_files('fixtures', self.rf, 3, self.sort_func)
        self.assertEqual(len(filenames), 3)

    def test_last_files_number_of_returned_files_2(self):
        """
        In our test data set there are only 5 suitable files, don't return
        more!
        """
        filenames = get_data.last_files('fixtures', self.rf, 6, self.sort_func)
        self.assertEqual(len(filenames), 5)

    def test_last_files_ordering_with_sort_function(self):
        """
        Make sure the files are ordered properly, as in we want the
        most recent one
        """
        filenames = get_data.last_files('fixtures', self.rf, 6, self.sort_func)
        self.assertEqual(filenames.index('fixtures/C1422466.123'), 4)
        self.assertEqual(filenames.index('fixtures/L1422366.510'), 3)
        self.assertEqual(filenames.index('fixtures/L1422366.105'), 2)
        self.assertEqual(filenames.index('fixtures/C1421953.787'), 1)
        self.assertEqual(filenames.index('fixtures/C1421953.747'), 0)

    def test_last_files_ordering_without_sort_function(self):
        """
        Without a sort function provided the order should be different:
        """
        filenames = get_data.last_files('fixtures', self.rf, 6, None)
        self.assertEqual(filenames.index('fixtures/L1422366.510'), 4)
        self.assertEqual(filenames.index('fixtures/L1422366.105'), 3)
        self.assertEqual(filenames.index('fixtures/C1422466.123'), 2)
        self.assertEqual(filenames.index('fixtures/C1421953.787'), 1)
        self.assertEqual(filenames.index('fixtures/C1421953.747'), 0)

    def test_validate_datapoint_correct_dp(self):
        self.assertTrue(get_data.validate_datapoint('(a 1234567890 123)'))

    def test_validate_datapoint_wrong_number_of_items_in_dp(self):
        self.assertFalse(get_data.validate_datapoint('(a 1234567890)'))

    def test_validate_datapoint_more_than_one_value(self):
        self.assertTrue(get_data.validate_datapoint('(a 1234567890 123 124)'))
        self.assertTrue(get_data.validate_datapoint('(a 1234567890 1 2 3)'))

    def test_get_datapoints(self):
        points = get_data.get_datapoints('fixtures/C1421953.787')
        expected = ['a 1421953787 44', 'a 1421953792 105',
                    'c 1421953793 160', 'a 1421953797 48',
                    'a 1421953802 49', 'c 1421953802 52']
        self.assertEqual(list(points), expected)

    def test_get_datapoints_from_file_with_faulty_dp_format(self):
        self.assertEqual(list(get_data.get_datapoints('fixtures/L1422366.105')),
                         [])

    def test_get_datapoints_from_file_with_several_lines(self):
        points = get_data.get_datapoints('fixtures/C1421953.747')
        expected = ['a 1421953747 49', 'a 1421953752 49', 'c 1421953753 102',
                    'a 1421953757 48', 'a 1421953758 49', 'a 1421953759 49',
                    'c 1421953760 102', 'a 1421953766 48']
        self.assertEqual(list(points), expected)

    def test_datadict(self):
        filenames = ['C1422466.123', # a datapoint with multiple values
                     'L1422366.105', # corrupt datapoint, should be ignored
                     'L1422366.510'] #
        filenames = [os.path.join('fixtures', f) for f in filenames]
        expected = {'a': {'time': ['1422366510', '1422366515',
                                   '1422366520'],
                          'line_0' : ['119', '119', '119']},
                    'b': {'time': ['1422466123'],
                          'line_0': ['456'],
                          'line_1': ['23']},
                    'c': {'time': ['1422366511', '1422366521'],
                          'line_0': ['120', '80']}}
        self.assertEqual(get_data.datadict(filenames), expected)

if __name__ == '__main__':
    unittest.main()
