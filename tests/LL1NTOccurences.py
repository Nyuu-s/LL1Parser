import unittest
from .LL1BaseGrammarHelper import BaseGrammerHelper

class LL1NTOccurencesMapSuite(BaseGrammerHelper):
    @classmethod
    def suite(cls):
        suite = unittest.TestSuite()
        suite.addTest(cls('test_grammar_video'))
        return suite 
    
    def setUp(self):
        return super().setUp()
    
    def test_grammar_video(self):
        _, input_grammar, expected = self.load_test_files(None, 'grammar_video')
        self._initialize_from_grammar_file(input_grammar)
        
        expected = {'T': {'Edash_optional_1', 'E'}, 'Edash': {'Edash_optional_1', 'E'}, 'Edash_optional_1': {'Edash'}, 'F': {'Tdash_optional_1', 'T'}, 'Tdash': {'Tdash_optional_1', 'T'}, 'Tdash_optional_1': {'Tdash'}, 'E': {'F_choice_1'}, 'F_choice_1': {'F'}}
         
        self.assert_dict(self.occurences_pack[0], expected)
 

            
