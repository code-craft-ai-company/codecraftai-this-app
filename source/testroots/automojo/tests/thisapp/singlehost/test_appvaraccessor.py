"""
    Testbase tests for :class:`AppVarAccessor` and :class:`VariableSet` under
    ``automojo.thisapp.appvaraccessor``.

    These were converted from a unittest module during the Phase 7
    unittest->testbase shift. Each test replicates the original ``setUp``
    behaviour (patching the shared ``AppVarAccessor._this_app`` class attribute
    with a stub application) at its start and the original ``tearDown``
    behaviour (restoring the original ``AppVarAccessor._this_app``) at its end
    via ``try``/``finally`` to preserve per-test isolation.
"""

import os
import sys

from typing import Any

TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)

from automojo.thisapp.appvaraccessor import AppVarAccessor, VariableSet
from automojo.thisapp.appvardesc import AppVarDesc


def create_stub_app(value: Any) -> Any:
    """
        Create a stub application object whose ``get_variable_value`` always
        returns ``value``.

        :param value: The value the stub application should resolve for any
            variable descriptor.

        :returns: A stub application instance.
    """
    class StubApp:
        def __init__(self, val: Any) -> None:
            self.values = {"value": val}
            return

        def get_variable_value(self, var_desc: Any) -> Any:
            rtnval = self.values["value"]
            return rtnval

    rtnval = StubApp(value)
    return rtnval


def _establish_thisapp_env() -> Any:
    """
        Replicate the original ``setUp``: capture the current
        ``AppVarAccessor._this_app`` so it can be restored, then patch it with
        a stub application that resolves variable values to ``"from-accessor"``.

        :returns: The original ``AppVarAccessor._this_app`` value, to be
            restored during teardown.
    """
    original_this_app = AppVarAccessor._this_app
    AppVarAccessor._this_app = create_stub_app(value="from-accessor")

    rtnval = original_this_app
    return rtnval


def _teardown_thisapp_env(original_this_app: Any) -> None:
    """
        Replicate the original ``tearDown``: restore the
        ``AppVarAccessor._this_app`` class attribute to its captured value.

        :param original_this_app: The value captured by
            :func:`_establish_thisapp_env`.
    """
    AppVarAccessor._this_app = original_this_app
    return


def test_init_requires_appvardesc() -> None:
    """
        Constructing an :class:`AppVarAccessor` with a non-:class:`AppVarDesc`
        argument must raise ``AssertionError``.
    """
    original_this_app = _establish_thisapp_env()
    try:
        raised = False
        try:
            AppVarAccessor(object())
        except AssertionError:
            raised = True
        assert raised
    finally:
        _teardown_thisapp_env(original_this_app=original_this_app)

    return


def test_set_name_mismatch_raises() -> None:
    """
        Binding an :class:`AppVarAccessor` to a class attribute whose name does
        not match the descriptor must raise ``AssertionError``.
    """
    original_this_app = _establish_thisapp_env()
    try:
        raised = False
        try:
            type("Holder", (), {"ACCESSOR": AppVarAccessor(AppVarDesc())})
        except AssertionError:
            raised = True
        assert raised
    finally:
        _teardown_thisapp_env(original_this_app=original_this_app)

    return


def test_accessor_retrieves_value() -> None:
    """
        Reading an :class:`AppVarAccessor` attribute must resolve the value via
        the patched application.
    """
    original_this_app = _establish_thisapp_env()
    try:
        class DescHolder:
            VAR_ONE = AppVarDesc()

        valid_desc = DescHolder.VAR_ONE

        class AccessHolder:
            VAR_ONE = AppVarAccessor(valid_desc)

        access = AccessHolder.VAR_ONE
        assert access == "from-accessor"
    finally:
        _teardown_thisapp_env(original_this_app=original_this_app)

    return


def test_accessor_set_not_allowed() -> None:
    """
        Setting an :class:`AppVarAccessor` attribute must raise
        ``AttributeError`` and must not alter the resolved read value.
    """
    original_this_app = _establish_thisapp_env()
    try:
        class DescHolder:
            VAR_TWO = AppVarDesc()

        valid_desc = DescHolder.VAR_TWO

        class AccessHolder:
            VAR_TWO = AppVarAccessor(valid_desc)

        accessor = AccessHolder.VAR_TWO
        raised = False
        try:
            AccessHolder.VAR_TWO.__set__(None, "value")
        except AttributeError:
            raised = True
        assert raised
        assert accessor == "from-accessor"
    finally:
        _teardown_thisapp_env(original_this_app=original_this_app)

    return


def test_variable_set_items_resolves_override_order() -> None:
    """
        :meth:`VariableSet.items` must resolve descriptor override order,
        preferring the derived definition and including extra descriptors.
    """
    original_this_app = _establish_thisapp_env()
    try:
        class BaseVars(VariableSet):
            BASE = AppVarDesc(section="BASE")

        class DerivedVars(BaseVars):
            BASE = AppVarDesc(section="DERIVED")
            EXTRA = AppVarDesc(section="EXTRA")

        items = DerivedVars.items()
        assert len(items) == 2
        assert items[0] is DerivedVars.BASE
        assert items[0].section == "DERIVED"
        assert items[1] is DerivedVars.EXTRA
    finally:
        _teardown_thisapp_env(original_this_app=original_this_app)

    return
