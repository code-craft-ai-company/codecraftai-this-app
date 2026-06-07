"""
    Testbase conversion of the ``ThisApplication`` unittest module.

    These tests exercise :class:`ThisApplication` construction guards, variable
    value precedence and conversion, environment/context override behaviour, and
    one-shot variable-set resolution. The original :class:`unittest.TestCase`
    ``setUp``/``tearDown`` backed up and restored ``os.environ`` to keep each
    test isolated from environment mutations performed by the others. That
    setup/teardown is replicated per test here via the
    :func:`_establish_thisapp_env` helper and a ``try``/``finally`` restore so
    the original isolation guarantees are preserved exactly.
"""

import os
import sys
import tempfile
import types


TEST_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "..",
        "packages",
    )
)
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)


def install_stub_semantic_error() -> type:
    """
        Install a stub ``automojo.errors.exceptions`` module providing a
        :class:`SemanticError` so the target module can import it without the
        full package being present.

        :returns: The stub :class:`SemanticError` class that was installed.
    """
    semantic_module = types.ModuleType("automojo.errors.exceptions")

    class SemanticError(Exception):
        pass

    semantic_module.SemanticError = SemanticError

    errors_pkg = types.ModuleType("automojo.errors")
    errors_pkg.__path__ = []
    errors_pkg.exceptions = semantic_module

    automojo_pkg = sys.modules.setdefault("automojo", types.ModuleType("automojo"))
    automojo_pkg.__path__ = []

    sys.modules["automojo.errors"] = errors_pkg
    sys.modules["automojo.errors.exceptions"] = semantic_module

    rtnval = SemanticError
    return rtnval


install_stub_semantic_error()

from automojo.thisapp import thisapplication as thisapplication_module
from automojo.thisapp.appvardesc import AppVarDesc
from automojo.thisapp.thisapplication import ThisApplication


def _establish_thisapp_env() -> dict:
    """
        Replicate the original ``setUp`` step by capturing a snapshot of the
        current process environment so it can be restored after the test runs.

        :returns: A snapshot dictionary of ``os.environ`` to restore later.
    """
    env_backup = dict(os.environ)
    return env_backup


def _restore_thisapp_env(env_backup: dict) -> None:
    """
        Replicate the original ``tearDown`` step by restoring the process
        environment from the snapshot captured in :func:`_establish_thisapp_env`.

        :param env_backup: The environment snapshot to restore.
    """
    os.environ.clear()
    os.environ.update(env_backup)
    return


def test_init_requires_establish_flag() -> None:
    """
        Constructing :class:`ThisApplication` without the establish-persona flag
        must raise a :class:`SemanticError`.
    """
    env_backup = _establish_thisapp_env()
    try:
        raised = False
        try:
            ThisApplication(
                name="TestApp",
                logger_name="log",
                log_basename="base",
                presence_dir="/tmp/app",
                log_directory="/tmp/app/logs",
                settings_file="settings.config",
                extensions="",
                service_name=None,
                context_insert=None,
            )
        except thisapplication_module.SemanticError:
            raised = True

        assert raised
    finally:
        _restore_thisapp_env(env_backup=env_backup)

    return


def test_get_variable_value_precedence_and_converter() -> None:
    """
        Environment values take precedence over settings-file values, and a
        supplied converter is applied to the resolved value.
    """
    env_backup = _establish_thisapp_env()
    try:
        with tempfile.TemporaryDirectory() as tempdir:
            settings_path = os.path.join(tempdir, "settings.config")
            with open(settings_path, "w", encoding="utf-8") as handle:
                handle.write("[MAIN]\nMY_VAR=settings\n")

            class VarDescHolder:
                MY_VAR = AppVarDesc(section="MAIN")

            desc = VarDescHolder.MY_VAR
            os.environ[desc.name] = "envvalue"

            this_app = ThisApplication(
                name="TestApp",
                logger_name="log",
                log_basename="base",
                presence_dir=tempdir,
                log_directory=os.path.join(tempdir, "logs"),
                settings_file=settings_path,
                extensions="",
                service_name=None,
                from_establish_app_persona=True,
            )

            value = this_app.get_variable_value(desc, default="default", converter=str.upper)
            assert value == "ENVVALUE"
            assert this_app.get_variable_value(desc) == "envvalue"
    finally:
        _restore_thisapp_env(env_backup=env_backup)

    return


def test_override_variable_value_sets_environment_and_context() -> None:
    """
        Overriding a variable value updates the application context, the process
        environment, and the value returned by ``get_variable_value``.
    """
    env_backup = _establish_thisapp_env()
    try:
        class VarDescHolder:
            VAR_A = AppVarDesc(context_path="context.var")

        desc = VarDescHolder.VAR_A
        this_app = ThisApplication(
            name="TestApp",
            logger_name="log",
            log_basename="base",
            presence_dir="/tmp/app",
            log_directory="/tmp/app/logs",
            settings_file="/tmp/app/settings.config",
            extensions="",
            service_name=None,
            from_establish_app_persona=True,
        )

        this_app.override_variable_value(desc, 42)

        assert this_app.get_variable_value(desc) == 42
        assert os.environ[desc.name] == "42"
        assert this_app.context.lookup("context.var") == 42
    finally:
        _restore_thisapp_env(env_backup=env_backup)

    return


def test_resolve_variable_set_resolves_each_variable_once() -> None:
    """
        Resolving a variable set populates the context with each variable's
        default value and resolves each variable only once even across repeated
        resolution calls.
    """
    env_backup = _establish_thisapp_env()
    try:
        class DescHolder:
            FIRST = AppVarDesc(context_path="first.path", default="1")
            SECOND = AppVarDesc(context_path="second.path", default="2")

        class VarSet:
            @classmethod
            def items(cls):
                return [DescHolder.FIRST, DescHolder.SECOND]

        this_app = ThisApplication(
            name="TestApp",
            logger_name="log",
            log_basename="base",
            presence_dir="/tmp/app",
            log_directory="/tmp/app/logs",
            settings_file="/tmp/app/settings.config",
            extensions="",
            service_name=None,
            from_establish_app_persona=True,
        )

        this_app.resolve_variable_set(VarSet)
        this_app.resolve_variable_set(VarSet)

        assert this_app.context.lookup("first.path") == "1"
        assert this_app.context.lookup("second.path") == "2"
        assert len(this_app._resolved_variables) == 2
    finally:
        _restore_thisapp_env(env_backup=env_backup)

    return
