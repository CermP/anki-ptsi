import unittest
import sys
import os

# Add scripts folder to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from utils import slugify

class TestUtils(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("Hello World"), "hello_world")
        self.assertEqual(slugify("Héllö Wörld"), "hello_world")
        self.assertEqual(slugify("  Spaces  "), "spaces")
        self.assertEqual(slugify("Special-Char_test"), "special_char_test")
        self.assertEqual(slugify("C'est l'été"), "cest_lete")

if __name__ == '__main__':
    unittest.main()
