"""
    Testbase tests for :mod:`automojo.thisapp.persona`.

    These tests verify the ``establish_app_persona`` behaviour: that it sets the
    expected ``AppPersona`` class attributes and the ``THISAPPLICATION_SINGLETON``
    on first call, and that a subsequent call returns the already-established
    singleton instead of replacing it.

    Each test re-establishes the shared persona/global state at the start (the
    former ``setUp``) and restores it at the end via ``try``/``finally`` (the
    former ``tearDown``) so that the module-level singleton and ``AppPersona``
    class attributes do not leak between tests.
"""

import os
import sys
import types


TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)


def install_stub_modules() -> type:
    """
        Install stub modules for the ``automojo`` packages required to import
        :mod:`automojo.thisapp.persona` in isolation.

        :returns: The stub ``SemanticError`` exception type.
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

    extension_pkg = types.ModuleType("automojo.extension")
    extension_pkg.__path__ = []
    sys.modules["automojo.extension"] = extension_pkg

    constants_module = types.ModuleType("automojo.extension.constants")
    constants_module.EXT_MOD_SEP = ";"
    sys.modules["automojo.extension.constants"] = constants_module

    factory_pkg = types.ModuleType("automojo.extension.factory")
    factory_pkg.__path__ = []
    sys.modules["automojo.extension.factory"] = factory_pkg

    superfactory_module = types.ModuleType("automojo.extension.factory.superfactory")

    class SuperFactory:
        def __init__(self, modules=None):
            self.modules = modules or []

    superfactory_module.SuperFactory = SuperFactory
    sys.modules["automojo.extension.factory.superfactory"] = superfactory_module

    rtnval = SemanticError
    return rtnval


SemanticError = install_stub_modules()

from automojo.thisapp import persona
from automojo.thisapp import wellknown
from automojo.thisapp.personavariables import PersonaVariablesDesc


def _establish_persona_env() -> None:
    """
        Replicate the former ``setUp``: reset the persona module global,
        the ``THISAPPLICATION_SINGLETON`` well-known global, and every
        ``AppPersona.AM_*`` class attribute so each test starts from a clean
        persona state.
    """
    persona.APP_PERSONA_ESTABLISHED = False
    wellknown.THISAPPLICATION_SINGLETON = None
    persona.AppPersona.AM_NAME = None
    persona.AppPersona.AM_LOGGER_NAME = None
    persona.AppPersona.AM_LOG_BASENAME = None
    persona.AppPersona.AM_PRESENCE_DIR = None
    persona.AppPersona.AM_LOG_DIRECTORY = None
    persona.AppPersona.AM_SETTINGS_FILENAME = None
    persona.AppPersona.AM_EXTENSIONS = None
    persona.AppPersona.AM_SERVICE_NAME = None
    return


def _teardown_persona_env() -> None:
    """
        Replicate the former ``tearDown``: clear the persona established flag
        and reset the ``THISAPPLICATION_SINGLETON`` well-known global so the
        established persona does not leak into the next test.
    """
    persona.APP_PERSONA_ESTABLISHED = False
    wellknown.THISAPPLICATION_SINGLETON = None
    return


def test_establish_app_persona_sets_values() -> None:
    """
        Establishing a persona for the first time must set the established
        flag, populate the ``AppPersona.AM_NAME`` class attribute, create the
        ``THISAPPLICATION_SINGLETON``, and expose the name through the
        singleton's persona variables.
    """
    _establish_persona_env()
    try:
        persona.establish_app_persona(
            name="DemoApp",
            logger_name="demo.logger",
            log_basename="demo",
            presence_dir="/tmp/demo",
            log_directory="/tmp/demo/logs",
            settings_file="settings.config",
            extensions="mod1;mod2",
            service_name="demo-service",
            context_insert=None,
        )

        assert persona.APP_PERSONA_ESTABLISHED
        assert persona.AppPersona.AM_NAME == "DemoApp"
        assert wellknown.THISAPPLICATION_SINGLETON is not None
        singleton_name = wellknown.THISAPPLICATION_SINGLETON.get_variable_value(
            PersonaVariablesDesc.AM_NAME
        )
        assert singleton_name == "DemoApp"
    finally:
        _teardown_persona_env()
    return


def test_establish_app_persona_subsequent_call_returns_existing() -> None:
    """
        A second call to ``establish_app_persona`` must not replace the
        already-established singleton; the ``THISAPPLICATION_SINGLETON`` must
        remain the instance created by the first call.
    """
    _establish_persona_env()
    try:
        persona.establish_app_persona(
            name="First",
            logger_name="logger",
            log_basename="base",
            presence_dir="/tmp/first",
            log_directory="/tmp/first/logs",
            settings_file="settings.config",
            extensions=None,
            service_name=None,
            context_insert=None,
        )

        first_app = wellknown.THISAPPLICATION_SINGLETON

        persona.establish_app_persona(
            name="Second",
            logger_name="logger2",
            log_basename="base2",
            presence_dir="/tmp/second",
            log_directory="/tmp/second/logs",
            settings_file="settings2.config",
            extensions=None,
            service_name=None,
            context_insert=None,
        )

        assert wellknown.THISAPPLICATION_SINGLETON is first_app
    finally:
        _teardown_persona_env()
    return
