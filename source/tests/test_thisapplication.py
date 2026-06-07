import os
import sys
import tempfile
import types
import unittest

TEST_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "packages"))
if TEST_ROOT not in sys.path:
    sys.path.insert(0, TEST_ROOT)


def install_stub_semantic_error():
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

    return SemanticError


install_stub_semantic_error()

from ccai.thisapp import thisapplication as thisapplication_module
from ccai.thisapp.appvardesc import AppVarDesc
from ccai.thisapp.thisapplication import ThisApplication


class TestThisApplication(unittest.TestCase):

    def setUp(self):
        self.env_backup = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_init_requires_establish_flag(self):
        with self.assertRaises(thisapplication_module.SemanticError):
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

    def test_get_variable_value_precedence_and_converter(self):
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
            self.assertEqual(value, "ENVVALUE")
            self.assertEqual(this_app.get_variable_value(desc), "envvalue")

    def test_override_variable_value_sets_environment_and_context(self):
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

        self.assertEqual(this_app.get_variable_value(desc), 42)
        self.assertEqual(os.environ[desc.name], "42")
        self.assertEqual(this_app.context.lookup("context.var"), 42)

    def test_resolve_variable_set_resolves_each_variable_once(self):
        
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

        self.assertEqual(this_app.context.lookup("first.path"), "1")
        self.assertEqual(this_app.context.lookup("second.path"), "2")
        self.assertEqual(len(this_app._resolved_variables), 2)


if __name__ == "__main__":
    unittest.main()
