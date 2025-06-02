
from .LL1BaseTestSuite import BaseTestSuite
import src.parsing.LL1.LL1ParsingTableMaker as Helper

class BaseGrammerHelper(BaseTestSuite):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
    

    def setUp(self):
        """Initialize common state shared across all tests"""
        self.tokens = None
        self.parsed_rules_map = None
        self.occurences_pack = None
        self.firsts_and_follows_pack = None
        self.has_optionals = None

    def _initialize_from_grammar_file(self, filename):
        """Load and initialize grammar from a file"""
        with open(filename, "r", encoding="utf-8") as file:
            grammar = file.read()
        self.tokens = Helper.tokenize(grammar)
        Helper.preprocess_tokens(self.tokens)
        self.parsed_rules_map, self.occurences_pack, \
            self.firsts_and_follows_pack, self.has_optionals = Helper.parse_grammar(self.tokens)
        
    def call_build_firsts(self):
        Helper.build_firsts_set(self.parsed_rules_map, self.firsts_and_follows_pack[0])
    def call_build_follows(self, start="S"):
        Helper.build_follow_set(start,self.parsed_rules_map, self.firsts_and_follows_pack[2], self.occurences_pack[0], self.firsts_and_follows_pack[0], self.firsts_and_follows_pack[1])
 