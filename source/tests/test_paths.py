import os
import shutil
import tempfile
import unittest
from unittest import mock

from ccai.thisapp import paths
from ccai.thisapp.enumerations import JobType
from ccai.thisapp.runtimevariables import RuntimeVariables, RuntimeVariablesDesc
from ccai.thisapp import wellknown
from ccai.thisapp.appvaraccessor import AppVarAccessor
from ccai.thisapp.thisapplication import ThisApplication


class PathsTestCase(unittest.TestCase):

    def setUp(self):
        self.workdir = tempfile.mkdtemp()
        self.presence_dir = os.path.join(self.workdir, "presence")
        self.output_dir = os.path.join(self.workdir, "output")
        self.shared_dir = os.path.join(self.workdir, "shared")
        os.makedirs(self.presence_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.shared_dir, exist_ok=True)

        self.env_patch = mock.patch.dict(os.environ, {}, clear=True)
        self.env_patch.start()

        AppVarAccessor._this_app = None

        self.context_store = {}
        self.this_app = ThisApplication(
            name="testruntime",
            logger_name="testruntime",
            log_basename="testruntime",
            presence_dir=self.presence_dir,
            log_directory=os.path.join(self.presence_dir, "logs"),
            settings_file=os.path.join(self.presence_dir, "settings.config"),
            extensions="",
            service_name=None,
            context_insert=self.context_store.__setitem__,
            from_establish_app_persona=True
        )
        wellknown.THISAPPLICATION_SINGLETON = self.this_app

        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, self.presence_dir)
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(self.presence_dir, "logs"))
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY, self.output_dir)
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_SHARED_STORE_DIRECTORY, self.shared_dir)
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_TESTS, os.path.join(self.output_dir, "testresults"))
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY, "True")
        self.this_app.override_variable_value(RuntimeVariablesDesc.AM_JOB_TYPE, JobType.TestRun.value)

        # reset cached directory globals
        self.prev_globals = {
            'DIR_PRESENCE_DIRECTORY': paths.DIR_PRESENCE_DIRECTORY,
            'DIR_CACHE_DIRECTORY': paths.DIR_CACHE_DIRECTORY,
            'DIR_DIAGNOSTICS_DIRECTORY': paths.DIR_DIAGNOSTICS_DIRECTORY,
            'DIR_RESULTS_DIRECTORY': paths.DIR_RESULTS_DIRECTORY,
            'DIR_SHARED_STORE_DIRECTORY': paths.DIR_SHARED_STORE_DIRECTORY,
            'DIR_TESTRESULTS_DIRECTORY': paths.DIR_TESTRESULTS_DIRECTORY,
            'DIR_TESTCASE_BYPRODUCTS_DIRECTORY': paths.DIR_TESTCASE_BYPRODUCTS_DIRECTORY,
        }
        paths.DIR_PRESENCE_DIRECTORY = None
        paths.DIR_CACHE_DIRECTORY = None
        paths.DIR_DIAGNOSTICS_DIRECTORY = None
        paths.DIR_RESULTS_DIRECTORY = None
        paths.DIR_SHARED_STORE_DIRECTORY = None
        paths.DIR_TESTRESULTS_DIRECTORY = None
        paths.DIR_TESTCASE_BYPRODUCTS_DIRECTORY = None

    def tearDown(self):
        shutil.rmtree(self.workdir, ignore_errors=True)
        wellknown.THISAPPLICATION_SINGLETON = None
        self.env_patch.stop()
        AppVarAccessor._this_app = None
        # restore globals
        paths.DIR_PRESENCE_DIRECTORY = self.prev_globals['DIR_PRESENCE_DIRECTORY']
        paths.DIR_CACHE_DIRECTORY = self.prev_globals['DIR_CACHE_DIRECTORY']
        paths.DIR_DIAGNOSTICS_DIRECTORY = self.prev_globals['DIR_DIAGNOSTICS_DIRECTORY']
        paths.DIR_RESULTS_DIRECTORY = self.prev_globals['DIR_RESULTS_DIRECTORY']
        paths.DIR_SHARED_STORE_DIRECTORY = self.prev_globals['DIR_SHARED_STORE_DIRECTORY']
        paths.DIR_TESTRESULTS_DIRECTORY = self.prev_globals['DIR_TESTRESULTS_DIRECTORY']
        paths.DIR_TESTCASE_BYPRODUCTS_DIRECTORY = self.prev_globals['DIR_TESTCASE_BYPRODUCTS_DIRECTORY']

    def test_collect_python_modules_depth_limit(self):
        root = os.path.join(self.workdir, "mods")
        os.makedirs(os.path.join(root, "sub", "deep"), exist_ok=True)
        # Create a sibling directory to 'sub' to ensure we don't abort early
        os.makedirs(os.path.join(root, "sub2"), exist_ok=True)

        with open(os.path.join(root, "m1.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(root, "sub", "m2.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(root, "sub", "deep", "m3.py"), "w") as f:
            f.write("pass")
        with open(os.path.join(root, "sub2", "m4.py"), "w") as f:
            f.write("pass")

        found = paths.collect_python_modules(root, max_depth=1)
        expected = {
            os.path.join(root, "m1.py"),
            os.path.join(root, "sub", "m2.py"),
            os.path.join(root, "sub2", "m4.py")
        }
        self.assertEqual(set(found), expected)

    def test_ensure_directory_is_package(self):
        pkg = os.path.join(self.workdir, "pkg")
        os.makedirs(pkg)
        paths.ensure_directory_is_package(pkg, package_title="Title")
        init_file = os.path.join(pkg, "__init__.py")
        self.assertTrue(os.path.exists(init_file))
        with open(init_file, "r") as f:
            contents = f.read()
        self.assertIn("Title", contents)

    def test_get_directory_for_code_container(self):
        import ccai.thisapp.paths as mod
        dpath = paths.get_directory_for_code_container(mod)
        self.assertTrue(dpath.endswith(os.path.join("ccai", "thisapp")))

    def test_normalize_name_for_path(self):
        name = "My Module: test,1.2;3"
        norm = paths.normalize_name_for_path(name)
        self.assertEqual(norm, "MyModuletest123")

    def test_get_temporary_directory_and_file(self):
        temp_dir = paths.get_temporary_directory()
        self.assertTrue(temp_dir.startswith(self.output_dir))
        tmp_file = paths.get_temporary_file(suffix=".txt", prefix="temp_")
        self.assertTrue(tmp_file.startswith(temp_dir))
        self.assertTrue(tmp_file.endswith(".txt"))

    def test_get_path_for_artifacts_created(self):
        label = "art"
        apath = paths.get_path_for_artifacts(label)
        self.assertTrue(apath.startswith(os.path.join(self.output_dir, "artifacts")))
        self.assertTrue(os.path.exists(apath))
