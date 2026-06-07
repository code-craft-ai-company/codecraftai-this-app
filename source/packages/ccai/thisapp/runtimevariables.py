"""
.. module:: runtimevariables
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains the :class:`AM_RUNTIME_VARIABLES`
              object which is used store the environment variables.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

import os

from datetime import datetime
from uuid import uuid4

from ccai.xmodules.xconvert import parse_bool
from ccai.xmodules.xdatetime import (
    parse_datetime, DATETIME_FORMAT_FILESYSTEM, DATETIME_FORMAT_TIMESTAMP
)
from ccai.xmodules.xlogging.levels import LogLevel

from ccai.thisapp.appvardesc import AppVarDesc
from ccai.thisapp.appvaraccessor import AppVarAccessor
from ccai.thisapp.contextpaths import ContextPaths
from ccai.thisapp.personavariables import PersonaVariablesDesc, PersonaVariables
from ccai.thisapp.wellknown import ThisApplicationSingleton


from ccai.thisapp.enumerations import JobType


class DefaultValue:
    NotSet = "(not-set)"

def default_template_path_for_tests():
    rtnval = os.path.join(RuntimeVariables.AM_PRESENCE_DIR, "results", "testresults", "%(starttime)s")
    return rtnval

def default_job_seed():
    rtnval = str(uuid4())
    return rtnval

class RuntimeVariablesDesc(PersonaVariablesDesc):

    AM_ACTIVATION_PROFILE = AppVarDesc(default=None)
    AM_AUTOMATION_POD = AppVarDesc(default=DefaultValue.NotSet)

    AM_BUG_SERVER_TYPE = AppVarDesc(default=None)
    AM_BUG_SERVER_ENDPOINT = AppVarDesc(default=None)
    AM_BUG_PROJECTS = AppVarDesc(default=None)
    AM_BUG_TEAM = AppVarDesc(default=None)
    AM_BUG_USERNAME = AppVarDesc(default=None)
    AM_BUG_TOKEN = AppVarDesc(default=None)

    AM_BUILD_RELEASE = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.BUILD_RELEASE)
    AM_BUILD_BRANCH = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.BUILD_BRANCH)
    AM_BUILD_FLAVOR = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.BUILD_FLAVOR)
    AM_BUILD_NAME = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.BUILD_NAME)
    AM_BUILD_URL = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.BUILD_URL)

    AM_DEBUG_BREAKPOINTS = AppVarDesc(default=None, context_path=ContextPaths.DEBUG_BREAKPOINTS)
    AM_DEBUG_DEBUGGER = AppVarDesc(default=None, context_path=ContextPaths.DEBUG_DEBUGGER)

    AM_DIAGNOSTICS_POSTRUN = AppVarDesc(default=None,  context_path=ContextPaths.DIAGNOSTICS_POSTRUN)
    AM_DIAGNOSTICS_PRERUN = AppVarDesc(default=None, context_path=ContextPaths.DIAGNOSTICS_PRERUN)
    AM_DIAGNOSTICS_TRACEBACK_POLICY_OVERRIDE = AppVarDesc(default=None, context_path=ContextPaths.DIAGNOSTICS_TRACEBACK_POLICY_OVERRIDE)

    AM_INTERACTIVE_CONSOLE = AppVarDesc(default=False)

    AM_RUN_ID = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.RUNID)

    AM_PIPELINE_ID = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.PIPELINE_ID)
    AM_PIPELINE_NAME = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.PIPELINE_NAME)
    AM_PIPELINE_INSTANCE = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.PIPELINE_INSTANCE)

    AM_JOB_CLASS = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_CLASS)
    AM_JOB_ID = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_ID)
    AM_JOB_INITIATOR = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_INITIATOR)
    AM_JOB_LABEL = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_LABEL)
    AM_JOB_NAME = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_NAME)
    AM_JOB_OWNER = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_OWNER)
    AM_JOB_SEED = AppVarDesc(default=default_job_seed, context_path=ContextPaths.JOB_SEED)
    AM_JOB_TAG = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_TAG)
    AM_JOB_TYPE = AppVarDesc(default=JobType.Unknown.value, context_path=ContextPaths.JOB_TYPE)
    AM_JOB_VENUE = AppVarDesc(default=DefaultValue.NotSet, context_path=ContextPaths.JOB_VENUE)

    AM_LOG_LEVEL_CONSOLE = AppVarDesc(default=LogLevel.WARNING, context_path=ContextPaths.LOGGING_LEVEL_CONSOLE)
    AM_LOG_LEVEL_FILE = AppVarDesc(default=LogLevel.DEBUG, context_path=ContextPaths.LOGGING_LEVEL_LOGFILE)

    AM_OUTPUT_DIRECTORY = AppVarDesc(default=None, context_path=ContextPaths.OUTPUT_DIRECTORY)

    AM_HAS_SHARED_OUTPUT_DIRECTORY = AppVarDesc(default=False, context_path=ContextPaths.OUTPUT_DIRECTORY_IS_SHARED)
    AM_SHARED_STORE_DIRECTORY = AppVarDesc(default=None, context_path=ContextPaths.SHARED_STORE_DIRECTORY)

    AM_RESULTS_STATIC_SUMMARY_TEMPLATE = AppVarDesc(default=None)
    AM_RESULTS_STATIC_RESOURCE_DEST_DIR = AppVarDesc(default=None)
    AM_RESULTS_STATIC_RESOURCE_SRC_DIR = AppVarDesc(default=None)

    AM_STARTTIME = AppVarDesc(default=datetime.now(), context_path=ContextPaths.STARTTIME)

    AM_TESTROOT = AppVarDesc(default=None, context_path=ContextPaths.TESTROOT)
    AM_TESTRUN_TIMEOUT = AppVarDesc(default=None)

    AM_TEMPLATE_PATH_FOR_ORCHESTRATION = AppVarDesc(default=None, context_path=ContextPaths.TEMPLATE_PATH_FOR_ORCHESTRATION)
    AM_TEMPLATE_PATH_FOR_SERVICES = AppVarDesc(default=None, context_path=ContextPaths.TEMPLATE_PATH_FOR_SERVICES)
    AM_TEMPLATE_PATH_FOR_TESTS = AppVarDesc(default=default_template_path_for_tests, context_path=ContextPaths.TEMPLATE_PATH_FOR_TESTS)
    AM_TEMPLATE_PATH_FOR_BUILD = AppVarDesc(default=None)

    AM_RESULT_PATH_FOR_ORCHESTRATION = AppVarDesc(default=None, context_path=ContextPaths.RESULT_PATH_FOR_ORCHESTRATION)
    AM_RESULT_PATH_FOR_SERVICES = AppVarDesc(default=None, context_path=ContextPaths.RESULT_PATH_FOR_SERVICES)
    AM_RESULT_PATH_FOR_TESTS = AppVarDesc(default=None, context_path=ContextPaths.RESULT_PATH_FOR_TESTS)
    AM_RESULT_PATH_FOR_BUILD = AppVarDesc(default=None)
    AM_RESULT_PATH_FOR_INFRASTRUCTURE = AppVarDesc(default=None)


class RuntimeVariables(PersonaVariables):
    """
        Container for all the configuration variables that can be passed via environmental variables.
    """

    AM_OUTPUT_DIRECTORY = AppVarAccessor(RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY)

    AM_HAS_SHARED_OUTPUT_DIRECTORY = AppVarAccessor(RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY)
    AM_SHARED_STORE_DIRECTORY = AppVarAccessor(RuntimeVariablesDesc.AM_SHARED_STORE_DIRECTORY)

    AM_ACTIVATION_PROFILE = AppVarAccessor(RuntimeVariablesDesc.AM_ACTIVATION_PROFILE)

    AM_AUTOMATION_POD = AppVarAccessor(RuntimeVariablesDesc.AM_AUTOMATION_POD)

    AM_BUG_SERVER_TYPE = AppVarAccessor(RuntimeVariablesDesc.AM_BUG_SERVER_TYPE)
    AM_BUG_SERVER_ENDPOINT = AppVarAccessor(RuntimeVariablesDesc.AM_BUG_SERVER_ENDPOINT)
    AM_BUG_PROJECTS = AppVarAccessor(RuntimeVariablesDesc.AM_BUG_PROJECTS)
    AM_BUG_TEAM = AppVarAccessor(RuntimeVariablesDesc.AM_BUG_TEAM)
    AM_BUG_USERNAME = AppVarAccessor(RuntimeVariablesDesc.AM_BUG_USERNAME)
    AM_BUG_TOKEN = AppVarAccessor(RuntimeVariablesDesc.AM_BUG_TOKEN)

    AM_BUILD_RELEASE = AppVarAccessor(RuntimeVariablesDesc.AM_BUILD_RELEASE)
    AM_BUILD_BRANCH = AppVarAccessor(RuntimeVariablesDesc.AM_BUILD_BRANCH)
    AM_BUILD_FLAVOR = AppVarAccessor(RuntimeVariablesDesc.AM_BUILD_FLAVOR)
    AM_BUILD_NAME = AppVarAccessor(RuntimeVariablesDesc.AM_BUILD_NAME)
    AM_BUILD_URL = AppVarAccessor(RuntimeVariablesDesc.AM_BUILD_URL)

    AM_DEBUG_BREAKPOINTS = AppVarAccessor(RuntimeVariablesDesc.AM_DEBUG_BREAKPOINTS)
    AM_DEBUG_DEBUGGER = AppVarAccessor(RuntimeVariablesDesc.AM_DEBUG_DEBUGGER)

    AM_DIAGNOSTICS_POSTRUN = AppVarAccessor(RuntimeVariablesDesc.AM_DIAGNOSTICS_POSTRUN)
    AM_DIAGNOSTICS_PRERUN = AppVarAccessor(RuntimeVariablesDesc.AM_DIAGNOSTICS_PRERUN)
    AM_DIAGNOSTICS_TRACEBACK_POLICY_OVERRIDE = AppVarAccessor(RuntimeVariablesDesc.AM_DIAGNOSTICS_TRACEBACK_POLICY_OVERRIDE)

    AM_INTERACTIVE_CONSOLE = AppVarAccessor(RuntimeVariablesDesc.AM_INTERACTIVE_CONSOLE)

    AM_RUN_ID = AppVarAccessor(RuntimeVariablesDesc.AM_RUN_ID)

    AM_PIPELINE_ID = AppVarAccessor(RuntimeVariablesDesc.AM_PIPELINE_ID)
    AM_PIPELINE_NAME = AppVarAccessor(RuntimeVariablesDesc.AM_PIPELINE_NAME)
    AM_PIPELINE_INSTANCE = AppVarAccessor(RuntimeVariablesDesc.AM_PIPELINE_INSTANCE)

    AM_JOB_CLASS = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_CLASS)
    AM_JOB_ID = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_ID)
    AM_JOB_TYPE = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_TYPE)
    AM_JOB_INITIATOR = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_INITIATOR)
    AM_JOB_LABEL = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_LABEL)
    AM_JOB_NAME = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_NAME)
    AM_JOB_OWNER = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_OWNER)
    AM_JOB_SEED = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_SEED)
    AM_JOB_TAG = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_TAG)
    AM_JOB_VENUE = AppVarAccessor(RuntimeVariablesDesc.AM_JOB_VENUE)

    AM_LOG_LEVEL_CONSOLE = AppVarAccessor(RuntimeVariablesDesc.AM_LOG_LEVEL_CONSOLE)
    AM_LOG_LEVEL_FILE = AppVarAccessor(RuntimeVariablesDesc.AM_LOG_LEVEL_FILE)

    AM_RESULTS_STATIC_SUMMARY_TEMPLATE = AppVarAccessor(RuntimeVariablesDesc.AM_RESULTS_STATIC_SUMMARY_TEMPLATE)
    AM_RESULTS_STATIC_RESOURCE_DEST_DIR = AppVarAccessor(RuntimeVariablesDesc.AM_RESULTS_STATIC_RESOURCE_DEST_DIR)
    AM_RESULTS_STATIC_RESOURCE_SRC_DIR = AppVarAccessor(RuntimeVariablesDesc.AM_RESULTS_STATIC_RESOURCE_SRC_DIR)

    AM_STARTTIME = AppVarAccessor(RuntimeVariablesDesc.AM_STARTTIME)

    AM_TESTROOT = AppVarAccessor(RuntimeVariablesDesc.AM_TESTROOT)
    AM_TESTRUN_TIMEOUT = AppVarAccessor(RuntimeVariablesDesc.AM_TESTRUN_TIMEOUT)

    AM_TEMPLATE_PATH_FOR_ORCHESTRATION = AppVarAccessor(RuntimeVariablesDesc.AM_TEMPLATE_PATH_FOR_ORCHESTRATION)
    AM_TEMPLATE_PATH_FOR_SERVICES = AppVarAccessor(RuntimeVariablesDesc.AM_TEMPLATE_PATH_FOR_SERVICES)
    AM_TEMPLATE_PATH_FOR_TESTS = AppVarAccessor(RuntimeVariablesDesc.AM_TEMPLATE_PATH_FOR_TESTS)
    AM_TEMPLATE_PATH_FOR_BUILD = AppVarAccessor(RuntimeVariablesDesc.AM_TEMPLATE_PATH_FOR_BUILD)

    AM_RESULT_PATH_FOR_ORCHESTRATION = AppVarAccessor(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_ORCHESTRATION)
    AM_RESULT_PATH_FOR_SERVICES = AppVarAccessor(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_SERVICES)
    AM_RESULT_PATH_FOR_TESTS = AppVarAccessor(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_TESTS)
    AM_RESULT_PATH_FOR_BUILD = AppVarAccessor(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_BUILD)
    AM_RESULT_PATH_FOR_INFRASTRUCTURE = AppVarAccessor(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_INFRASTRUCTURE)


def get_runtime_seed() -> str:
    rtnval = RuntimeVariables.AM_JOB_SEED
    return rtnval


RUNTIME_VARIABLES_RESOLVED = False

def resolve_runtime_variables():

    global RUNTIME_VARIABLES_RESOLVED

    if RUNTIME_VARIABLES_RESOLVED:
        return
    
    RUNTIME_VARIABLES_RESOLVED = True

    this_app = ThisApplicationSingleton()
    
    starttime_value = RuntimeVariables.AM_STARTTIME
    if isinstance(starttime_value, str):
        try:
            starttime_value = parse_datetime(starttime_value, DATETIME_FORMAT_TIMESTAMP)
        except ValueError:
            starttime_value = parse_datetime(starttime_value, DATETIME_FORMAT_FILESYSTEM)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_STARTTIME, starttime_value)

    shared_output_directory = RuntimeVariables.AM_HAS_SHARED_OUTPUT_DIRECTORY
    if isinstance(shared_output_directory, str):
        try:
            shared_output_directory = parse_bool(shared_output_directory)
        except ValueError:
            shared_output_directory = RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY.default
    this_app.override_variable_value(RuntimeVariablesDesc.AM_HAS_SHARED_OUTPUT_DIRECTORY, shared_output_directory)

    this_app.resolve_variable_set(RuntimeVariablesDesc)

    return
