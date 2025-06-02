import unittest
from .LL1BaseTestSuite import BaseTestSuite
from src.parsing.LL1.Cobarse import LL1Parser
from src.parsing.LL1.LL1ParsingTableMaker import EGrammarToken
from src.parsing.LL1.Coblex import lex
class LL1ParsingResultSuite(BaseTestSuite):
    @classmethod
    def suite(cls):
        suite = unittest.TestSuite()
        suite.addTest(cls('test_grammar_video'))
        return suite 
    
    def setUp(self):
        return super().setUp()
    
    def test_grammar_video(self):
        in_data, input_grammar, expected = self.load_test_files('test_data_1', 'grammar_video')
        
        parser = LL1Parser(lex(in_data), "E")
        parser.compute_lookup_table(input_grammar)
        expected = parser.start()
         
        self.assertTrue(expected, "Parsing failed")
            
