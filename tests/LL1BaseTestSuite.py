from pathlib import Path
import unittest

class BaseTestSuite(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.inputs_dir = Path(__file__).parent / 'inputs'
    
    
    def load_test_files(self, data_file, in_grammar ):
        input_file = None
        input_grammar_file = None
        expected_file = None
        if data_file != None:
            input_file = self.inputs_dir / f'{data_file}.in' 
            expected_file = self.inputs_dir / f'{data_file}.out'
        if in_grammar != None:
            input_grammar_file = self.inputs_dir / f'{in_grammar}.gm'
        return input_file, input_grammar_file, expected_file
    
    def assert_dict(self, obj, expected):
        self.assertDictEqual(obj, expected, f"First map do not match expected\n{obj}")