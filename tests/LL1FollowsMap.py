import unittest
from .LL1BaseGrammarHelper import BaseGrammerHelper
from src.parsing.LL1.LL1ParsingTableMaker import EGrammarToken

class LL1FollowsMapSuite(BaseGrammerHelper):
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
        self.call_build_firsts()
        self.call_build_follows("E")
        
        expected = {'E': {(EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$')}, 'Edash': {(EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$')}, 'Edash_optional_1': {(EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$')}, 'T': {(EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$'), (EGrammarToken.TERMINAL, '+')}, 'Tdash': {(EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$'), (EGrammarToken.TERMINAL, '+')}, 'Tdash_optional_1': {(EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$'), (EGrammarToken.TERMINAL, '+')}, 'F': {(EGrammarToken.TERMINAL, '*'), (EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$'), (EGrammarToken.TERMINAL, '+')}, 'F_choice_1': {(EGrammarToken.TERMINAL, '*'), (EGrammarToken.TERMINAL, ')'), (EGrammarToken.PUNCTUATION, '$'), (EGrammarToken.TERMINAL, '+')}}
        self.assert_dict(self.firsts_and_follows_pack[1], expected)
 
    

