"""
    Testbase conversion of the ``ccai.thisapp.paths`` unittest module.

    Each test reconstructs the shared ThisApplication environment via the
    module-level ``_establish_thisapp_env`` helper (the former ``setUp``) and
    tears it down with a ``try``/``finally`` block (the former ``tearDown``) so
    that the singleton and cached directory globals stay isolated between tests.
"""

import os
import shutil
import tempfile
from dataclasses import dataclass, field
from typing import Dict
from unittest import mock

from ccai.thisapp import paths
from ccai.thisapp.enumerations import JobType
from ccai.thisapp.runtimevariables import RuntimeVariables, RuntimeVariablesDesc
from ccai.thisapp import wellknown
from ccai.thisapp.appvaraccessor import AppVarAccessor
from ccai.thisapp.thisapplication import ThisApplication


@dataclass
class ThisAppEnv:
    """
        Container for the objects produced by ``_establish_thisapp_env`` so a
        test can both exercise the application and tear the environment down.
    """

    workdir: str
    presence_dir: str
    output_dir: str
    shared_dir: str
    this_app: ThisApplication
    context_store: Dict[str, object]
    env_patch: object
    prev_globals: Dict[str, object] = field(default_factory=dict)


def _establish_thisapp_env() -> ThisAppEnv:
    """
        Build the shared ThisApplication test environment (the former
        ``setUp``): create the temporary directory tree, patch ``os.environ``,
        construct the application singleton, override the runtime variables and
        reset the cached ``paths.DIR_*`` globals.

        :returns: A populated :class:`ThisAppEnv` describing the environment.
    """
    workdir = tempfile.mkdtemp()
    presence_dir = os.path.join(workdir, "presence")
    output_dir = os.path.join(workdir, "output")
    shared_dir = os.path.join(workdir, "shared")
    os.makedirs(presence_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(shared_dir, exist_ok=True)

    env_patch = mock.patch.dict(os.environ, {}, clear=True)
    env_patch.start()

    AppVarAccessor._this_app = None

    context_store = {}
    this_app = ThisApplication(
        name="testruntime",
        logger_name="testruntime",
        log_basename="testruntime",
        presence_dir=presence_dir,
        log_directory=os.path.join(presence_dir, "logs"),
        settings_file=os.path.join(presence_dir, "settings.config"),
        extensions="",
        service_name=None,
        context_insert=context_store.__setitem__,
        from_establish_app_persona=True
    )
    wellknown.THISAPPLICATION_SINGLETON = this_app

    this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, presence_dir)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(presence_dir, "logs"))
    this_app.override_variable_value(RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY, output_dir)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_SHARED_STORE_DIRECTORY, shared_dir)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_TESTS, os.path.join(output_dir, "testresults"))
    this_app.override_variable_value(RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY, "True")
    this_app.override_variable_value(RuntimeVariablesDesc.AM_JOB_TYPE, JobType.TestRun.value)

    # reset cached directory globals
    prev_globals = {
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

    env = ThisAppEnv(
        workdir=workdir,
        presence_dir=presence_dir,
        output_dir=output_dir,
        shared_dir=shared_dir,
        this_app=this_app,
        context_store=context_store,
        env_patch=env_patch,
        prev_globals=prev_globals
    )
    return env


def _teardown_thisapp_env(env: ThisAppEnv) -> None:
    """
        Tear down the shared ThisApplication test environment (the former
        ``tearDown``): remove the temporary directory, clear the singleton, stop
        the ``os.environ`` patch and restore the cached ``paths.DIR_*`` globals.

        :param env: The environment returned by ``_establish_thisapp_env``.
    """
    shutil.rmtree(env.workdir, ignore_errors=True)
    wellknown.THISAPPLICATION_SINGLETON = None
    env.env_patch.stop()
    AppVarAccessor._this_app = None
    # restore globals
    paths.DIR_PRESENCE_DIRECTORY = env.prev_globals['DIR_PRESENCE_DIRECTORY']
    paths.DIR_CACHE_DIRECTORY = env.prev_globals['DIR_CACHE_DIRECTORY']
    paths.DIR_DIAGNOSTICS_DIRECTORY = env.prev_globals['DIR_DIAGNOSTICS_DIRECTORY']
    paths.DIR_RESULTS_DIRECTORY = env.prev_globals['DIR_RESULTS_DIRECTORY']
    paths.DIR_SHARED_STORE_DIRECTORY = env.prev_globals['DIR_SHARED_STORE_DIRECTORY']
    paths.DIR_TESTRESULTS_DIRECTORY = env.prev_globals['DIR_TESTRESULTS_DIRECTORY']
    paths.DIR_TESTCASE_BYPRODUCTS_DIRECTORY = env.prev_globals['DIR_TESTCASE_BYPRODUCTS_DIRECTORY']
    return


def test_collect_python_modules_depth_limit() -> None:
    """
        Verify ``collect_python_modules`` honours ``max_depth`` while still
        descending across sibling directories.
    """
    env = _establish_thisapp_env()
    try:
        root = os.path.join(env.workdir, "mods")
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
        assert set(found) == expected
    finally:
        _teardown_thisapp_env(env)
    return


def test_ensure_directory_is_package() -> None:
    """
        Verify ``ensure_directory_is_package`` creates an ``__init__.py`` that
        carries the supplied package title.
    """
    env = _establish_thisapp_env()
    try:
        pkg = os.path.join(env.workdir, "pkg")
        os.makedirs(pkg)
        paths.ensure_directory_is_package(pkg, package_title="Title")
        init_file = os.path.join(pkg, "__init__.py")
        assert os.path.exists(init_file)
        with open(init_file, "r") as f:
            contents = f.read()
        assert "Title" in contents
    finally:
        _teardown_thisapp_env(env)
    return


def test_get_directory_for_code_container() -> None:
    """
        Verify ``get_directory_for_code_container`` resolves a module to its
        owning runtime directory.
    """
    env = _establish_thisapp_env()
    try:
        import ccai.thisapp.paths as mod
        dpath = paths.get_directory_for_code_container(mod)
        assert dpath.endswith(os.path.join("ccai", "thisapp"))
    finally:
        _teardown_thisapp_env(env)
    return


def test_normalize_name_for_path() -> None:
    """
        Verify ``normalize_name_for_path`` strips path-hostile punctuation and
        whitespace.
    """
    env = _establish_thisapp_env()
    try:
        name = "My Module: test,1.2;3"
        norm = paths.normalize_name_for_path(name)
        assert norm == "MyModuletest123"
    finally:
        _teardown_thisapp_env(env)
    return


def test_get_temporary_directory_and_file() -> None:
    """
        Verify the temporary directory and file helpers root themselves under
        the configured output directory and honour the requested affixes.
    """
    env = _establish_thisapp_env()
    try:
        temp_dir = paths.get_temporary_directory()
        assert temp_dir.startswith(env.output_dir)
        tmp_file = paths.get_temporary_file(suffix=".txt", prefix="temp_")
        assert tmp_file.startswith(temp_dir)
        assert tmp_file.endswith(".txt")
    finally:
        _teardown_thisapp_env(env)
    return


def test_get_path_for_artifacts_created() -> None:
    """
        Verify ``get_path_for_artifacts`` returns an existing path under the
        output ``artifacts`` directory.
    """
    env = _establish_thisapp_env()
    try:
        label = "art"
        apath = paths.get_path_for_artifacts(label)
        assert apath.startswith(os.path.join(env.output_dir, "artifacts"))
        assert os.path.exists(apath)
    finally:
        _teardown_thisapp_env(env)
    return
