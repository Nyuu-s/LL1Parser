import unittest
import os

class LL1TestCase(unittest.TestCase):
    def setUp(self):
        input_folder = f"./inputs/{self.__class__.__name__}"
        if not os.path.exists(input_folder):
            self.assertTrue(False, f"{input_folder} does not exist")
            
