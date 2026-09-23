import os
import shutil
import tempfile
import unittest
import unittest.mock
from datetime import datetime

from ccai.thisapp import activation
from ccai.xmodules.xlogging import activation as loggingactivation

from ccai.thisapp.contextpaths import ContextPaths
from ccai.thisapp.enumerations import JobType
from ccai.thisapp.runtimevariables import RuntimeVariables, RuntimeVariablesDesc
from ccai.thisapp import wellknown
from ccai.thisapp.appvaraccessor import AppVarAccessor
from ccai.thisapp.thisapplication import ThisApplication


class ActivationProfileTests(unittest.TestCase):

    def setUp(self):
        self._saved_env = os.environ.copy()

        self.env_patch = unittest.mock.patch.dict(os.environ, {}, clear=True)
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

        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, self.temp_dir)
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(self.temp_dir, "logs"))
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_BASENAME, "testruntime")
        self.this_app._application_variables[RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY.key] = os.path.join(self.temp_dir, "output")
        self.this_app._application_variables[RuntimeVariablesDesc.AM_STARTTIME.key] = datetime.now()

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

        loggingactivation.ACTIVATED_INFO = None

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._saved_env)
        self.env_patch.stop()
        AppVarAccessor._this_app = None
        wellknown.THISAPPLICATION_SINGLETON = None
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        return

    def test_activate_runtime_dispatches(self):
        with unittest.mock.patch.object(activation, '_activate_profile_common') as mock_console:
            activation.activate_profile_console()
            mock_console.assert_called_once()

        return

    def test_activate_profile_service_requires_service_name(self):

        self.this_app._service_name = None
        with self.assertRaises(activation.SemanticError):
            activation.activate_profile_service()

        return

    def test_activate_profile_service_uses_configured_name(self):

        self.this_app._service_name = 'testsvc'
        activation.activate_profile_service()
        expected_output_dir = os.path.join(self.temp_dir, "services", self.this_app.service_name)
        self.assertEqual(expected_output_dir, RuntimeVariables.AM_OUTPUT_DIRECTORY)

        return


class ActivationCommonTests(unittest.TestCase):

    def setUp(self):

        self.temp_dir = tempfile.mkdtemp()
        self.context_store = {}

        self.env_patch = unittest.mock.patch.dict(os.environ, {}, clear=True)
        self.env_patch.start()

        AppVarAccessor._this_app = None

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

        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, self.temp_dir)
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(self.temp_dir, "logs"))
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_BASENAME, "testruntime")
        self.this_app._application_variables[RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY.key] = os.path.join(self.temp_dir, "output")
        self.this_app._application_variables[RuntimeVariablesDesc.AM_STARTTIME.key] = datetime.now()

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

        loggingactivation.ACTIVATED_INFO = None

        return

    def tearDown(self):

        wellknown.THISAPPLICATION_SINGLETON = None
        self.env_patch.stop()
        AppVarAccessor._this_app = None
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        return

    def test_activate_profile_job_output_directory_template(self):

        fixed_time = datetime(2020, 1, 1, 1, 1, 1)
        self.this_app._application_variables[RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY.key] = None
        self.this_app._application_variables[RuntimeVariablesDesc.AM_STARTTIME.key] = fixed_time

        activation.activate_profile_job(job_type=JobType.TestRun)

        found = self.this_app.context.lookup(ContextPaths.OUTPUT_DIRECTORY, default=None)

        self.assertIsNotNone(found)

        return
