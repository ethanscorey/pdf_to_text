import unittest

from pdftk import PDFTK
from magick import Magick
from tesseract import Tesseract


class TestSetup(unittest.TestCase):
    def test_pdftk_exists(self):
        self.assertEqual(PDFTK().run().returncode, 0)

    def test_magick_exists(self):
        self.assertEqual(Magick().run().returncode, 0)

    def test_tesseract_exists(self):
        self.assertEqual(Tesseract().run().returncode, 0)
