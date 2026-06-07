"""
    Testbase conversion of the ``thisapp`` activation tests.

    These tests exercise the activation-profile dispatch helpers in
    :mod:`automojo.thisapp.activation`. They require heavy shared setup
    (a temp directory, a cleared ``os.environ`` patched via
    :func:`unittest.mock.patch.dict`, a constructed :class:`ThisApplication`
    assigned to ``wellknown.THISAPPLICATION_SINGLETON`` with overridden
    ``RuntimeVariables`` and reset module globals). The shared setup and
    teardown are replicated per test (via :func:`_establish_thisapp_env`
    and a ``try/finally`` cleanup) to preserve the per-test isolation that
    the original ``unittest.TestCase.setUp``/``tearDown`` pair provided.
"""

import os
import shutil
import tempfile
from typing import Any, Callable, Dict, Optional
from unittest import mock
from datetime import datetime

from automojo.thisapp import activation
from automojo.xmodules.xdatetime import DATETIME_FORMAT_FILESYSTEM
from automojo.xmodules.xlogging import activation as loggingactivation

from automojo.thisapp.contextpaths import ContextPaths
from automojo.thisapp.enumerations import ActivationProfile, JobType
from automojo.thisapp.runtimevariables import RuntimeVariables, RuntimeVariablesDesc
from automojo.thisapp import wellknown
from automojo.thisapp.appvaraccessor import AppVarAccessor
from automojo.thisapp.thisapplication import ThisApplication


class ThisAppEnv:
    """
        A small namespace bundling the objects produced by
        :func:`_establish_thisapp_env` that a converted test needs to run
        and to tear itself down faithfully.
    """

    def __init__(
        self,
        this_app: ThisApplication,
        temp_dir: str,
        context_store: Dict[str, Any],
        env_patch: Any,
        saved_env: Optional[Dict[str, str]]
    ) -> None:
        """
            Initialize the environment namespace.

            :param this_app: The constructed :class:`ThisApplication` singleton.
            :param temp_dir: The temp directory backing the presence/log/output dirs.
            :param context_store: The dict capturing context inserts.
            :param env_patch: The started ``mock.patch.dict`` handle for ``os.environ``.
            :param saved_env: A copy of ``os.environ`` captured before patching,
                              or ``None`` when the test does not restore it.
        """
        self.this_app = this_app
        self.temp_dir = temp_dir
        self.context_store = context_store
        self.env_patch = env_patch
        self.saved_env = saved_env
        return


def _establish_thisapp_env(save_environ: bool) -> ThisAppEnv:
    """
        Replicate the shared ``setUp`` logic of the original activation
        test cases: clear/patch ``os.environ``, reset the
        ``AppVarAccessor`` cache, create a temp directory, construct a
        :class:`ThisApplication`, assign it as the singleton, override the
        runtime variables, install the simplified ``get_variable_value``
        accessor and reset the logging-activation global.

        :param save_environ: When ``True`` a copy of ``os.environ`` is taken
                             before patching so it can be restored during
                             teardown (matching ``ActivationProfileTests``);
                             when ``False`` no copy is taken (matching
                             ``ActivationCommonTests``).

        :returns: A :class:`ThisAppEnv` carrying the objects the test needs.
    """
    saved_env = None
    if save_environ is True:
        saved_env = os.environ.copy()

    env_patch = mock.patch.dict(os.environ, {}, clear=True)
    env_patch.start()

    AppVarAccessor._this_app = None

    temp_dir = tempfile.mkdtemp()
    context_store = {}

    this_app = ThisApplication(
        name="testruntime",
        logger_name="testruntime",
        log_basename="testruntime",
        presence_dir=temp_dir,
        log_directory=os.path.join(temp_dir, "logs"),
        settings_file=os.path.join(temp_dir, "settings.config"),
        extensions="",
        service_name=None,
        context_insert=context_store.__setitem__,
        from_establish_app_persona=True
    )
    wellknown.THISAPPLICATION_SINGLETON = this_app

    this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, temp_dir)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(temp_dir, "logs"))
    this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_BASENAME, "testruntime")
    this_app._application_variables[RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY.key] = os.path.join(temp_dir, "output")
    this_app._application_variables[RuntimeVariablesDesc.AM_STARTTIME.key] = datetime.now()

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

    this_app.get_variable_value = simple_get.__get__(this_app, ThisApplication)

    loggingactivation.ACTIVATED_INFO = None

    env = ThisAppEnv(
        this_app=this_app,
        temp_dir=temp_dir,
        context_store=context_store,
        env_patch=env_patch,
        saved_env=saved_env
    )
    return env


def _teardown_thisapp_env(env: ThisAppEnv) -> None:
    """
        Replicate the shared ``tearDown`` logic of the original activation
        test cases: optionally restore ``os.environ`` from the saved copy,
        stop the env patch, reset the ``AppVarAccessor`` cache, clear the
        :class:`ThisApplication` singleton and remove the temp directory.

        :param env: The :class:`ThisAppEnv` returned by
                    :func:`_establish_thisapp_env`.
    """
    if env.saved_env is not None:
        os.environ.clear()
        os.environ.update(env.saved_env)

    if env.saved_env is not None:
        env.env_patch.stop()
        AppVarAccessor._this_app = None
        wellknown.THISAPPLICATION_SINGLETON = None
        shutil.rmtree(env.temp_dir, ignore_errors=True)
    else:
        wellknown.THISAPPLICATION_SINGLETON = None
        env.env_patch.stop()
        AppVarAccessor._this_app = None
        shutil.rmtree(env.temp_dir, ignore_errors=True)

    return


def test_activate_runtime_dispatches() -> None:
    """
        Verify that ``activate_profile_console`` dispatches through the shared
        ``_activate_profile_common`` helper exactly once.
    """
    env = _establish_thisapp_env(save_environ=True)
    try:
        with mock.patch.object(activation, '_activate_profile_common') as mock_console:
            activation.activate_profile_console()
            mock_console.assert_called_once()
    finally:
        _teardown_thisapp_env(env)

    return


def test_activate_profile_service_requires_service_name() -> None:
    """
        Verify that ``activate_profile_service`` raises ``SemanticError`` when
        no service name has been configured on the application.
    """
    env = _establish_thisapp_env(save_environ=True)
    try:
        env.this_app._service_name = None

        raised = False
        try:
            activation.activate_profile_service()
        except activation.SemanticError:
            raised = True

        assert raised
    finally:
        _teardown_thisapp_env(env)

    return


def test_activate_profile_service_uses_configured_name() -> None:
    """
        Verify that ``activate_profile_service`` builds the output directory
        from the configured service name.
    """
    env = _establish_thisapp_env(save_environ=True)
    try:
        env.this_app._service_name = 'testsvc'
        activation.activate_profile_service()
        expected_output_dir = os.path.join(env.temp_dir, "services", env.this_app.service_name)
        assert expected_output_dir == RuntimeVariables.AM_OUTPUT_DIRECTORY
    finally:
        _teardown_thisapp_env(env)

    return


def test_activate_profile_job_output_directory_template() -> None:
    """
        Verify that ``activate_profile_job`` populates the output-directory
        context entry from the start-time template when the output directory
        has not yet been resolved.
    """
    env = _establish_thisapp_env(save_environ=False)
    try:
        fixed_time = datetime(2020, 1, 1, 1, 1, 1)
        env.this_app._application_variables[RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY.key] = None
        env.this_app._application_variables[RuntimeVariablesDesc.AM_STARTTIME.key] = fixed_time

        activation.activate_profile_job(job_type=JobType.TestRun)

        found = env.this_app.context.lookup(ContextPaths.OUTPUT_DIRECTORY, default=None)

        assert found is not None
    finally:
        _teardown_thisapp_env(env)

    return
