"""
    Testbase conversion of the ``RuntimeVariables`` unittest module.

    These tests exercise the resolution of runtime variables in
    ``ccai.thisapp.runtimevariables``. Each test establishes a fully
    isolated ``ThisApplication`` environment (patched ``os.environ``, a temp
    presence/log directory, the ``wellknown.THISAPPLICATION_SINGLETON``
    binding, baseline persona overrides, a reset of the
    ``RUNTIME_VARIABLES_RESOLVED`` module global, and a stubbed
    ``get_variable_value`` accessor) and tears it down at the end so that the
    singleton and module-level globals never leak between tests.
"""

import os
import shutil
import tempfile
from datetime import datetime
from unittest import mock

from ccai.thisapp import runtimevariables
from ccai.thisapp.runtimevariables import RuntimeVariablesDesc, DefaultValue
from ccai.thisapp import wellknown
from ccai.thisapp.appvaraccessor import AppVarAccessor
from ccai.thisapp.thisapplication import ThisApplication


class _ThisAppEnv:
    """
        A small namespace bundling the objects produced by the per-test
        environment setup so they can be passed back to each test and torn
        down faithfully.
    """

    def __init__(
        self,
        this_app: ThisApplication,
        temp_dir: str,
        context_store: dict,
        env_patch: object,
        prev_resolved: bool
    ) -> None:
        """
            Capture the per-test environment objects.

            :param this_app: The constructed ``ThisApplication`` instance.
            :param temp_dir: The temporary presence/log directory.
            :param context_store: The dict backing ``context_insert``.
            :param env_patch: The started ``mock.patch.dict`` for ``os.environ``.
            :param prev_resolved: The prior value of
                ``runtimevariables.RUNTIME_VARIABLES_RESOLVED``.
        """
        self.this_app = this_app
        self.temp_dir = temp_dir
        self.context_store = context_store
        self.env_patch = env_patch
        self.prev_resolved = prev_resolved
        return


def _establish_thisapp_env() -> _ThisAppEnv:
    """
        Replicate the original ``setUp``: patch ``os.environ`` clear, reset the
        ``AppVarAccessor`` singleton, create a temp presence/log directory,
        build a ``ThisApplication`` persona, bind it as the wellknown
        singleton, apply baseline persona overrides, reset the runtime-variable
        resolution module global, forget the resolved runtime variables, and
        stub ``get_variable_value`` with the original ``simple_get`` accessor.

        :returns: A ``_ThisAppEnv`` carrying the objects each test needs and
            the state required to tear the environment back down.
    """
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

    # Set baseline persona values required by the variable accessors
    this_app.override_variable_value(RuntimeVariablesDesc.AM_PRESENCE_DIR, temp_dir)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, os.path.join(temp_dir, "logs"))

    # Reset the resolution of runtime variables so tests can recall 'runtimevariables.resolve_runtime_variables'
    prev_resolved = runtimevariables.RUNTIME_VARIABLES_RESOLVED
    runtimevariables.RUNTIME_VARIABLES_RESOLVED = False
    this_app.forget_variable(runtimevariables.RuntimeVariablesDesc.AM_STARTTIME)
    this_app.forget_variable(runtimevariables.RuntimeVariablesDesc.AM_JOB_SEED)
    this_app.forget_variable(runtimevariables.RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY)

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

    rtnval = _ThisAppEnv(
        this_app=this_app,
        temp_dir=temp_dir,
        context_store=context_store,
        env_patch=env_patch,
        prev_resolved=prev_resolved
    )
    return rtnval


def _teardown_thisapp_env(env: _ThisAppEnv) -> None:
    """
        Replicate the original cleanups (in LIFO order relative to ``setUp``):
        clear the wellknown singleton and the ``AppVarAccessor`` singleton,
        restore the ``RUNTIME_VARIABLES_RESOLVED`` module global, stop the
        ``os.environ`` patch, and remove the temp directory.

        :param env: The environment bundle returned by
            ``_establish_thisapp_env``.
    """
    wellknown.THISAPPLICATION_SINGLETON = None
    AppVarAccessor._this_app = None
    runtimevariables.RUNTIME_VARIABLES_RESOLVED = env.prev_resolved
    env.env_patch.stop()
    shutil.rmtree(env.temp_dir, ignore_errors=True)
    return


def test_get_runtime_seed_returns_expected_value() -> None:
    """
        A seed overridden on the application persona is returned verbatim by
        ``get_runtime_seed``.
    """
    env = _establish_thisapp_env()
    try:
        env.this_app.override_variable_value(RuntimeVariablesDesc.AM_JOB_SEED, 'myseed')
        assert 'myseed' == runtimevariables.get_runtime_seed()
    finally:
        _teardown_thisapp_env(env=env)
    return


def test_resolve_generates_seed_when_not_set() -> None:
    """
        When no seed is supplied, accessing the resolved ``AM_JOB_SEED`` value
        yields a generated seed rather than the ``DefaultValue.NotSet`` sentinel.
    """
    env = _establish_thisapp_env()
    try:
        seed = runtimevariables.RuntimeVariables.AM_JOB_SEED
        assert seed != DefaultValue.NotSet
    finally:
        _teardown_thisapp_env(env=env)
    return


def test_resolve_uses_environment_seed() -> None:
    """
        A seed supplied via the ``AM_JOB_SEED`` environment variable is honored
        when runtime variables are resolved.
    """
    env = _establish_thisapp_env()
    try:
        with mock.patch.dict(os.environ, {'AM_JOB_SEED': 'seed123'}, clear=True):
            runtimevariables.resolve_runtime_variables()
            found = runtimevariables.RuntimeVariables.AM_JOB_SEED
            assert 'seed123' == found
    finally:
        _teardown_thisapp_env(env=env)
    return


def test_resolve_parses_starttime_timestamp() -> None:
    """
        An ``AM_STARTTIME`` ISO timestamp from the environment is parsed into a
        ``datetime`` when runtime variables are resolved.
    """
    env = _establish_thisapp_env()
    try:
        start_time = '2025-01-02T03:04:05.123456'
        with mock.patch.dict(os.environ, {'AM_STARTTIME': start_time}, clear=True):
            runtimevariables.resolve_runtime_variables()
            found = runtimevariables.RuntimeVariables.AM_STARTTIME
            assert isinstance(found, datetime)
    finally:
        _teardown_thisapp_env(env=env)
    return


def test_resolve_parses_shared_output_directory_bool() -> None:
    """
        An ``AM_HAS_SHARED_OUTPUT_DIRECTORY`` truthy string from the environment
        is parsed into a boolean ``True`` when runtime variables are resolved.
    """
    env = _establish_thisapp_env()
    try:
        with mock.patch.dict(os.environ, {'AM_HAS_SHARED_OUTPUT_DIRECTORY': 'true'}, clear=True):
            runtimevariables.resolve_runtime_variables()
            found = runtimevariables.RuntimeVariables.AM_HAS_SHARED_OUTPUT_DIRECTORY
            assert found
    finally:
        _teardown_thisapp_env(env=env)
    return
