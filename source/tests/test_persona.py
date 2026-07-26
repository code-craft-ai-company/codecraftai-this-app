import os
import sys
import types
import unittest

TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)


def install_stub_modules():
    semantic_module = types.ModuleType("ccai.errors.exceptions")
    class SemanticError(Exception):
        pass
    semantic_module.SemanticError = SemanticError

    errors_pkg = types.ModuleType("ccai.errors")
    errors_pkg.__path__ = []
    errors_pkg.exceptions = semantic_module

    ccai_pkg = sys.modules.setdefault("ccai", types.ModuleType("ccai"))
    ccai_pkg.__path__ = []

    sys.modules["ccai.errors"] = errors_pkg
    sys.modules["ccai.errors.exceptions"] = semantic_module

    extension_pkg = types.ModuleType("ccai.extension")
    extension_pkg.__path__ = []
    sys.modules["ccai.extension"] = extension_pkg

    constants_module = types.ModuleType("ccai.extension.constants")
    constants_module.EXT_MOD_SEP = ";"
    sys.modules["ccai.extension.constants"] = constants_module

    factory_pkg = types.ModuleType("ccai.extension.factory")
    factory_pkg.__path__ = []
    sys.modules["ccai.extension.factory"] = factory_pkg

    superfactory_module = types.ModuleType("ccai.extension.factory.superfactory")
    class SuperFactory:
        def __init__(self, modules=None):
            self.modules = modules or []
    superfactory_module.SuperFactory = SuperFactory
    sys.modules["ccai.extension.factory.superfactory"] = superfactory_module

    return SemanticError


SemanticError = install_stub_modules()

from ccai.thisapp import persona
from ccai.thisapp import wellknown
from ccai.thisapp.personavariables import PersonaVariablesDesc


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
        )

        self.assertIs(wellknown.THISAPPLICATION_SINGLETON, first_app)

    def test_default_presence_dir_is_absolute_and_expanded(self):
        persona.establish_app_persona(
            name="DemoApp",
            logger_name="demo.logger",
            log_basename="demo",
        )

        presence = persona.AppPersona.AM_PRESENCE_DIR
        self.assertTrue(os.path.isabs(presence),
                        "The default presence dir must be absolute; the relative '~/<name>' "
                        "join made every derived path land under a literal '~/' directory "
                        "inside the current working directory.")
        self.assertNotIn("~", presence)
        self.assertEqual(persona.AppPersona.AM_LOG_DIRECTORY, os.path.join(presence, "logs"))

    def test_explicit_tilde_presence_dir_is_expanded(self):
        persona.establish_app_persona(
            name="DemoApp",
            logger_name="demo.logger",
            log_basename="demo",
            presence_dir=os.path.join("~", "demoapp-presence"),
        )

        presence = persona.AppPersona.AM_PRESENCE_DIR
        self.assertTrue(os.path.isabs(presence))
        self.assertNotIn("~", presence)

    def test_unknown_keyword_arguments_raise(self):
        # 'home_dir' instead of 'presence_dir' was silently swallowed for
        # months; the application then ran with a default it never chose.
        with self.assertRaises(SemanticError) as context:
            persona.establish_app_persona(
                name="DemoApp",
                logger_name="demo.logger",
                log_basename="demo",
                home_dir="/tmp/somewhere",
            )
        self.assertIn("home_dir", str(context.exception))
        self.assertFalse(persona.APP_PERSONA_ESTABLISHED,
                         "A rejected call must not establish the persona.")

    def test_unknown_keyword_arguments_raise_even_when_established(self):
        # The guard runs before the already-established short-circuit, so a
        # SECOND caller with a typo is told about it instead of silently
        # no-opping.
        persona.establish_app_persona(
            name="DemoApp",
            logger_name="demo.logger",
            log_basename="demo",
        )
        with self.assertRaises(SemanticError):
            persona.establish_app_persona(
                name="OtherApp",
                logger_name="other.logger",
                log_basename="other",
                extension_modules="some.module",
            )


if __name__ == "__main__":
    unittest.main()
