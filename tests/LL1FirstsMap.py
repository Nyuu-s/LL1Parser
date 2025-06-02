
import unittest
import src.parsing.LL1.LL1ParsingTableMaker as Helper

from .LL1BaseGrammarHelper import BaseGrammerHelper
from src.parsing.LL1.Cobarse import LL1Parser
from src.parsing.LL1.LL1ParsingTableMaker import EGrammarToken
from src.parsing.LL1.Coblex import lex


class LL1FirstsMapSuite(BaseGrammerHelper):
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
        expected = {'E': [(EGrammarToken.TERMINAL, '('), (EGrammarToken.TERMINAL, 'id')], 'Edash_optional_1': [(EGrammarToken.TERMINAL, '+'), (EGrammarToken.EPSILON, None)], 'Edash': [(EGrammarToken.EPSILON, None), (EGrammarToken.TERMINAL, '+')], 'T': [(EGrammarToken.TERMINAL, 'id'), (EGrammarToken.TERMINAL, '(')], 'Tdash_optional_1': [(EGrammarToken.TERMINAL, '*'), (EGrammarToken.EPSILON, None)], 'Tdash': [(EGrammarToken.EPSILON, None), (EGrammarToken.TERMINAL, '*')], 'F_choice_1': [(EGrammarToken.TERMINAL, 'id'), (EGrammarToken.TERMINAL, '(')], 'F': [(EGrammarToken.TERMINAL, '('), (EGrammarToken.TERMINAL, 'id')]}

        self.assert_dict(self.firsts_and_follows_pack[0], expected) 
    


        