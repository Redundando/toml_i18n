import unittest
from toml_i18n import TomlI18n, i18n

class TestI18n(unittest.TestCase):
    def test_initialization(self):
        TomlI18n.initialize(locale="en")
        self.assertTrue(TomlI18n.is_initialized())

    def test_get_translation(self):
        TomlI18n.initialize(locale="en")
        self.assertEqual(i18n("general.greeting", name="Alice"), "Missing translation for 'general.greeting'")

if __name__ == "__main__":
    unittest.main()
