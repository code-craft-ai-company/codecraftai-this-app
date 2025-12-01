import os
import sys
import types
import unittest

TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)


def install_stub_modules():
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

    return SemanticError


SemanticError = install_stub_modules()

from automojo.thisapp import persona
from automojo.thisapp import wellknown
from automojo.thisapp.personavariables import PersonaVariablesDesc


class TestPersona(unittest.TestCase):

    def setUp(self):
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

    def tearDown(self):
        persona.APP_PERSONA_ESTABLISHED = False
        wellknown.THISAPPLICATION_SINGLETON = None

    def test_establish_app_persona_sets_values(self):
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

        self.assertTrue(persona.APP_PERSONA_ESTABLISHED)
        self.assertEqual(persona.AppPersona.AM_NAME, "DemoApp")
        self.assertIsNotNone(wellknown.THISAPPLICATION_SINGLETON)
        self.assertEqual(
            wellknown.THISAPPLICATION_SINGLETON.get_variable_value(PersonaVariablesDesc.AM_NAME),
            "DemoApp",
        )

    def test_establish_app_persona_subsequent_call_returns_existing(self):
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

        self.assertIs(wellknown.THISAPPLICATION_SINGLETON, first_app)


if __name__ == "__main__":
    unittest.main()
