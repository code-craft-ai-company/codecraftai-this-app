import os
import sys
import types
import unittest

# Ensure the package path is available for imports
TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)

from automojo.thisapp.appvardesc import (
    AppVarDesc,
    VariableSource,
    assert_section_name,
    assert_variable_name,
)


class TestAppVarDesc(unittest.TestCase):

    def test_assert_section_name_valid(self):
        section = "MainSection"
        self.assertEqual(assert_section_name(section), section)

    def test_assert_section_name_invalid_inputs(self):
        with self.assertRaises(AssertionError):
            assert_section_name(123)
        with self.assertRaises(AssertionError):
            assert_section_name("   ")
        with self.assertRaises(AssertionError):
            assert_section_name(" invalid")
        with self.assertRaises(AssertionError):
            assert_section_name("bad[section]")

    def test_assert_variable_name_validation(self):
        self.assertEqual(assert_variable_name("VALID_NAME"), "VALID_NAME")
        with self.assertRaises(AssertionError):
            assert_variable_name(3.14)
        with self.assertRaises(AssertionError):
            assert_variable_name("")
        with self.assertRaises(AssertionError):
            assert_variable_name("9INVALID")

    def test_appvardesc_set_name_and_repr(self):
        class SampleVars:
            SAMPLE = AppVarDesc(section="SAMPLE_SECTION", default="value")

        var_desc = SampleVars.SAMPLE
        self.assertEqual(var_desc.name, "SAMPLE")
        self.assertEqual(var_desc.section, "SAMPLE_SECTION")
        self.assertEqual(var_desc.key, "SAMPLE_SECTION->SAMPLE")
        self.assertEqual(repr(var_desc), "AppVarDesc(name='SAMPLE', section='SAMPLE_SECTION')")
        self.assertEqual(str(var_desc), "SAMPLE")

    def test_variable_source_flag_values(self):
        self.assertTrue(VariableSource.ENVIRONMENT & VariableSource.BOTH)
        self.assertTrue(VariableSource.SETTINGS & VariableSource.BOTH)
        self.assertEqual(VariableSource.NONE.value, 0)


if __name__ == "__main__":
    unittest.main()
