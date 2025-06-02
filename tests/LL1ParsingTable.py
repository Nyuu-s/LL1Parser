import unittest
from .LL1BaseTestSuite import BaseTestSuite
from src.parsing.LL1.Cobarse import LL1Parser
from src.parsing.LL1.LL1ParsingTableMaker import EGrammarToken
class LL1ParsingTableSuite(BaseTestSuite):
    @classmethod
    def suite(cls):
        suite = unittest.TestSuite()
        suite.addTest(cls('test_grammar_video'))
        return suite 
    
    def setUp(self):
        return super().setUp()
    
    def test_grammar_video(self):
        _, input_grammar, expected = self.load_test_files(None, 'grammar_video')
        
        parser = LL1Parser([], "E")
        parser.compute_lookup_table(input_grammar)
        expected = {'E': {(EGrammarToken.TERMINAL, '('): [(EGrammarToken.NON_TERMINAL, 'T'), (EGrammarToken.NON_TERMINAL, 'Edash')], (EGrammarToken.TERMINAL, 'id'): [(EGrammarToken.NON_TERMINAL, 'T'), (EGrammarToken.NON_TERMINAL, 'Edash')]}, 'Edash': {(EGrammarToken.TERMINAL, ')'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.PUNCTUATION, '$'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.TERMINAL, '+'): [(EGrammarToken.NON_TERMINAL, 'Edash_optional_1')]}, 'Edash_optional_1': {(EGrammarToken.TERMINAL, '+'): [(EGrammarToken.TERMINAL, '+'), (EGrammarToken.NON_TERMINAL, 'T'), (EGrammarToken.NON_TERMINAL, 'Edash')], (EGrammarToken.TERMINAL, ')'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.PUNCTUATION, '$'): [(EGrammarToken.EPSILON, None)]}, 'T': {(EGrammarToken.TERMINAL, 'id'): [(EGrammarToken.NON_TERMINAL, 'F'), (EGrammarToken.NON_TERMINAL, 'Tdash')], (EGrammarToken.TERMINAL, '('): [(EGrammarToken.NON_TERMINAL, 'F'), (EGrammarToken.NON_TERMINAL, 'Tdash')]}, 'Tdash': {(EGrammarToken.TERMINAL, ')'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.PUNCTUATION, '$'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.TERMINAL, '+'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.TERMINAL, '*'): [(EGrammarToken.NON_TERMINAL, 'Tdash_optional_1')]}, 'Tdash_optional_1': {(EGrammarToken.TERMINAL, '*'): [(EGrammarToken.TERMINAL, '*'), (EGrammarToken.NON_TERMINAL, 'F'), (EGrammarToken.NON_TERMINAL, 'Tdash')], (EGrammarToken.TERMINAL, ')'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.PUNCTUATION, '$'): [(EGrammarToken.EPSILON, None)], (EGrammarToken.TERMINAL, '+'): [(EGrammarToken.EPSILON, None)]}, 'F': {(EGrammarToken.TERMINAL, '('): [(EGrammarToken.NON_TERMINAL, 'F_choice_1')], (EGrammarToken.TERMINAL, 'id'): [(EGrammarToken.NON_TERMINAL, 'F_choice_1')]}, 'F_choice_1': {(EGrammarToken.TERMINAL, 'id'): [(EGrammarToken.TERMINAL, 'id')], (EGrammarToken.TERMINAL, '('): [(EGrammarToken.GROUP, [(EGrammarToken.TERMINAL, '('), (EGrammarToken.NON_TERMINAL, 'E'), (EGrammarToken.TERMINAL, ')')])]}}
         
        self.assert_dict(parser.parse_table, expected)
 

