import unittest
import io
import xmlrunner
from .LL1FirstsMap import LL1FirstsMapSuite
from .LL1FollowsMap import LL1FollowsMapSuite
from .LL1NTOccurences import LL1NTOccurencesMapSuite
from .LL1ParsingTable import LL1ParsingTableSuite
from .LL1ParsingResult import LL1ParsingResultSuite

def run_all_suites():
    suites = [
        LL1FirstsMapSuite.suite(),
        LL1FollowsMapSuite.suite(),
        LL1NTOccurencesMapSuite.suite(),
        LL1ParsingTableSuite.suite(),
        LL1ParsingResultSuite.suite()
        
        # Add other suites here
    ]
    alltests = unittest.TestSuite(suites)
    # runner = unittest.TextTestRunner(verbosity=2)
    runner = xmlrunner.XMLTestRunner('tests/reports')
    for x in alltests:
        runner.run(x)

if __name__ == '__main__':
    run_all_suites()
