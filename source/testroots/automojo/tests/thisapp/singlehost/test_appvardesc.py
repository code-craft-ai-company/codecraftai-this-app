"""
    Testbase tests for the ``automojo.thisapp.appvardesc`` module.

    These tests cover the ``AppVarDesc`` descriptor, the ``VariableSource``
    flag enumeration, and the ``assert_section_name`` / ``assert_variable_name``
    validation helpers. Converted from the original ``unittest`` module to the
    testbase plain-function format (bare ``assert`` -> Failure, any other
    exception -> Error). The original module declared no ``setUp`` / ``tearDown``
    fixtures, so there is no per-test environment to establish or tear down.
"""

import os
import sys

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


def test_assert_section_name_valid() -> None:
    """
        A well-formed section name is returned unchanged by
        ``assert_section_name``.
    """
    section = "MainSection"
    assert assert_section_name(section) == section
    return


def test_assert_section_name_invalid_inputs() -> None:
    """
        ``assert_section_name`` rejects non-string, blank, leading-space, and
        bracket-bearing section names by raising ``AssertionError``.
    """
    raised = False
    try:
        assert_section_name(123)
    except AssertionError:
        raised = True
    assert raised

    raised = False
    try:
        assert_section_name("   ")
    except AssertionError:
        raised = True
    assert raised

    raised = False
    try:
        assert_section_name(" invalid")
    except AssertionError:
        raised = True
    assert raised

    raised = False
    try:
        assert_section_name("bad[section]")
    except AssertionError:
        raised = True
    assert raised
    return


def test_assert_variable_name_validation() -> None:
    """
        ``assert_variable_name`` returns valid names unchanged and rejects
        non-string, empty, and digit-leading names by raising ``AssertionError``.
    """
    assert assert_variable_name("VALID_NAME") == "VALID_NAME"

    raised = False
    try:
        assert_variable_name(3.14)
    except AssertionError:
        raised = True
    assert raised

    raised = False
    try:
        assert_variable_name("")
    except AssertionError:
        raised = True
    assert raised

    raised = False
    try:
        assert_variable_name("9INVALID")
    except AssertionError:
        raised = True
    assert raised
    return


def test_appvardesc_set_name_and_repr() -> None:
    """
        ``AppVarDesc`` resolves its name via ``__set_name__``, composes its
        ``key`` from section and name, and renders the expected ``repr`` / ``str``.
    """
    class SampleVars:
        SAMPLE = AppVarDesc(section="SAMPLE_SECTION", default="value")

    var_desc = SampleVars.SAMPLE
    assert var_desc.name == "SAMPLE"
    assert var_desc.section == "SAMPLE_SECTION"
    assert var_desc.key == "SAMPLE_SECTION->SAMPLE"
    assert repr(var_desc) == "AppVarDesc(name='SAMPLE', section='SAMPLE_SECTION')"
    assert str(var_desc) == "SAMPLE"
    return


def test_variable_source_flag_values() -> None:
    """
        ``VariableSource.BOTH`` carries both the ``ENVIRONMENT`` and
        ``SETTINGS`` flags, and ``VariableSource.NONE`` has a zero value.
    """
    assert VariableSource.ENVIRONMENT & VariableSource.BOTH
    assert VariableSource.SETTINGS & VariableSource.BOTH
    assert VariableSource.NONE.value == 0
    return
