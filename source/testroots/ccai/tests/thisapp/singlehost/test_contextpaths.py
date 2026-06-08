"""
    Testbase conversion of the ``ContextPaths`` enum unit tests.

    These tests verify that the ``ccai.thisapp.contextpaths.ContextPaths``
    enumeration exposes the expected well-known context path members and that
    each member carries its expected string value. Each test is an independent
    module-level ``test_*`` function; assertions use bare ``assert`` so an
    ``AssertionError`` is reported as a Failure and any other exception as an
    Error.
"""

from ccai.thisapp.contextpaths import ContextPaths


def test_result_path_for_build() -> None:
    """
        The ``ContextPaths`` enum must expose a ``RESULT_PATH_FOR_BUILD``
        member whose value is the well-known build results context path.
    """
    assert hasattr(ContextPaths, 'RESULT_PATH_FOR_BUILD')
    assert ContextPaths.RESULT_PATH_FOR_BUILD.value == "/configuration/runtime/paths/results/build"
    return
