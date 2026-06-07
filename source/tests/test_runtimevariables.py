import os
import shutil
import tempfile
import unittest
from datetime import datetime
from unittest import mock

from ccai.thisapp import runtimevariables
from ccai.thisapp.runtimevariables import RuntimeVariablesDesc, DefaultValue
from ccai.thisapp import wellknown
from ccai.thisapp.appvaraccessor import AppVarAccessor
from ccai.thisapp.thisapplication import ThisApplication

class RuntimeVariablesTests(unittest.TestCase):

    def setUp(self):
        self.env_patch = mock.patch.dict(os.environ, {}, clear=True)
        self.env_patch.start()

        AppVarAccessor._this_app = None

        self.temp_dir = tempfile.mkdtemp()
        self.context_store = {}

        self.this_app = ThisApplication(
            name="testruntime",
            logger_name="testruntime",
            log_basename="testruntime",
            presence_dir=self.temp_dir,
            log_directory=os.path.join(self.temp_dir, "logs"),
            settings_file=os.path.join(self.temp_dir, "settings.config"),
            extensions="",
            service_name=None,
            context_insert=self.context_store.__setitem__,
            from_establish_app_persona=True
        )
        wellknown.THISAPPLICATION_SINGLETON = self.this_app

        # Set baseline persona values required by the variable accessors
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, self.temp_dir)
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(self.temp_dir, "logs"))

        # Reset the resolution of runtime variables so tests can recall 'runtimevariables.resolve_runtime_variables'
        runtimevariables.RUNTIME_VARIABLES_RESOLVED = False
        self.this_app.forget_variable(runtimevariables.RuntimeVariablesDesc.AM_STARTTIME)
        self.this_app.forget_variable(runtimevariables.RuntimeVariablesDesc.AM_JOB_SEED)
        self.this_app.forget_variable(runtimevariables.RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY)

        def simple_get(self_app, variable_desc, default=None, converter=None):
            vkey = variable_desc.key
            if vkey not in self_app._application_variables:
                val = os.environ.get(variable_desc.name, variable_desc.default if variable_desc.default is not None else default)
                self_app._application_variables[vkey] = val
            else:
                val = self_app._application_variables[vkey]

            if converter is not None and val is not None:
                val = converter(val)

            return val

        self.this_app.get_variable_value = simple_get.__get__(self.this_app, ThisApplication)

        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        self.addCleanup(self._clear_singleton)
        self.addCleanup(self.env_patch.stop)
        return

    def _clear_singleton(self):
        wellknown.THISAPPLICATION_SINGLETON = None
        AppVarAccessor._this_app = None

    def test_get_runtime_seed_returns_expected_value(self):
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_JOB_SEED, 'myseed')
        self.assertEqual('myseed', runtimevariables.get_runtime_seed())

    def test_resolve_generates_seed_when_not_set(self):
        seed = runtimevariables.RuntimeVariables.AM_JOB_SEED
        self.assertNotEqual(seed, DefaultValue.NotSet)

    def test_resolve_uses_environment_seed(self):
        with mock.patch.dict(os.environ, {'AM_JOB_SEED': 'seed123'}, clear=True):
            runtimevariables.resolve_runtime_variables()
            found = runtimevariables.RuntimeVariables.AM_JOB_SEED
            self.assertEqual('seed123', found)

    def test_resolve_parses_starttime_timestamp(self):
        start_time = '2025-01-02T03:04:05.123456'
        with mock.patch.dict(os.environ, {'AM_STARTTIME': start_time}, clear=True):
            runtimevariables.resolve_runtime_variables()
            found = runtimevariables.RuntimeVariables.AM_STARTTIME
            self.assertIsInstance(found, datetime)

    def test_resolve_parses_shared_output_directory_bool(self):
        with mock.patch.dict(os.environ, {'AM_HAS_SHARED_OUTPUT_DIRECTORY': 'true'}, clear=True):
            runtimevariables.resolve_runtime_variables()
            found = runtimevariables.RuntimeVariables.AM_HAS_SHARED_OUTPUT_DIRECTORY
            self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
