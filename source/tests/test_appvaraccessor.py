import os
import sys
import types
import unittest

TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)

from ccai.thisapp.appvaraccessor import AppVarAccessor, VariableSet
from ccai.thisapp.appvardesc import AppVarDesc


def create_stub_app(value):
    class StubApp:
        def __init__(self, val):
            self.values = {"value": val}

        def get_variable_value(self, var_desc):
            return self.values["value"]

    return StubApp(value)


class TestAppVarAccessor(unittest.TestCase):

    def setUp(self):
        self.original_this_app = AppVarAccessor._this_app
        AppVarAccessor._this_app = create_stub_app("from-accessor")

    def tearDown(self):
        AppVarAccessor._this_app = self.original_this_app

    def test_init_requires_appvardesc(self):
        with self.assertRaises(AssertionError):
            AppVarAccessor(object())

    def test_set_name_mismatch_raises(self):
        with self.assertRaises(AssertionError):
            type("Holder", (), {"ACCESSOR": AppVarAccessor(AppVarDesc())})

    def test_accessor_retrieves_value(self):
        class DescHolder:
            VAR_ONE = AppVarDesc()

        valid_desc = DescHolder.VAR_ONE

        class AccessHolder:
            VAR_ONE = AppVarAccessor(valid_desc)

        access = AccessHolder.VAR_ONE
        self.assertEqual(access, "from-accessor")

    def test_accessor_set_not_allowed(self):
        class DescHolder:
            VAR_TWO = AppVarDesc()

        valid_desc = DescHolder.VAR_TWO

        class AccessHolder:
            VAR_TWO = AppVarAccessor(valid_desc)

        accessor = AccessHolder.VAR_TWO
        with self.assertRaises(AttributeError):
            AccessHolder.VAR_TWO.__set__(None, "value")
        self.assertEqual(accessor, "from-accessor")

    def test_variable_set_items_resolves_override_order(self):
        class BaseVars(VariableSet):
            BASE = AppVarDesc(section="BASE")

        class DerivedVars(BaseVars):
            BASE = AppVarDesc(section="DERIVED")
            EXTRA = AppVarDesc(section="EXTRA")

        items = DerivedVars.items()
        self.assertEqual(len(items), 2)
        self.assertIs(items[0], DerivedVars.BASE)
        self.assertEqual(items[0].section, "DERIVED")
        self.assertIs(items[1], DerivedVars.EXTRA)


if __name__ == "__main__":
    unittest.main()
