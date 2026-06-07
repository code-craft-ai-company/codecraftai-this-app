"""
.. module:: activation
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module which contains methods that implement the activation process.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Optional

import os
import tempfile
import uuid

from ccai.errors.exceptions import ConfigurationError, SemanticError
from ccai.errors.xtraceback import (
    TRACEBACK_CONFIG,
    VALID_MEMBER_TRACE_POLICY,
)

from ccai.xmodules.xlogging.levels import LogLevel

from ccai.thisapp.thisapplication import ThisApplication
from ccai.thisapp.wellknown import ThisApplicationSingleton

from ccai.xmodules.xlogging.parameters import LoggingLocation, LoggingReduction
from ccai.xmodules.xlogging.activation import (
    activate_standard_file_logging,
    activate_interactive_console_logging,
    activate_service_logging
)

from ccai.thisapp.enumerations import ActivationProfile, JobType
from ccai.thisapp.runtimevariables import RuntimeVariables, RuntimeVariablesDesc, DefaultValue


def activate_profile_command():

    # Guard against attemps to activate more than one, activation profile.
    if RuntimeVariables.AM_ACTIVATION_PROFILE is not None:
        errmsg = "An attempt was made to activate multiple environment activation profiles. profile={}".format(
            RuntimeVariables.AM_ACTIVATION_PROFILE
        )
        raise SemanticError(errmsg)

    this_app = ThisApplicationSingleton()

    this_app.override_variable_value(RuntimeVariablesDesc.AM_ACTIVATION_PROFILE, ActivationProfile.Command)
    
    _activate_profile_common(this_app)

    log_directory = RuntimeVariables.AM_LOG_DIRECTORY
    log_basename = RuntimeVariables.AM_LOG_BASENAME

    logging_location = LoggingLocation(log_directory, log_basename)

    console_level = RuntimeVariables.AM_LOG_LEVEL_CONSOLE
    file_level = RuntimeVariables.AM_LOG_LEVEL_FILE

    activate_standard_file_logging(logging_location, console_level, file_level)

    return


def activate_profile_console():

    # Guard against attemps to activate more than one, activation profile.
    if RuntimeVariables.AM_ACTIVATION_PROFILE is not None:
        errmsg = "An attempt was made to activate multiple environment activation profiles. profile={}".format(
            RuntimeVariables.AM_ACTIVATION_PROFILE
        )
        raise SemanticError(errmsg)

    this_app = ThisApplicationSingleton()

    this_app.override_variable_value(RuntimeVariablesDesc.AM_ACTIVATION_PROFILE, ActivationProfile.Console)
    

    temp_output_dir = tempfile.mkdtemp()
    this_app.override_variable_value(RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY, temp_output_dir)

    def showlog():

        print("OUTPUT FOLDER: {}".format(RuntimeVariables.AM_OUTPUT_DIRECTORY))
        print("")

        return

    log_directory = RuntimeVariables.AM_LOG_DIRECTORY
    log_basename = RuntimeVariables.AM_LOG_BASENAME

    logging_location = LoggingLocation(log_directory, log_basename)

    file_level = RuntimeVariables.AM_LOG_LEVEL_CONSOLE

    _activate_profile_common(this_app)

    activate_interactive_console_logging(logging_location, file_level)

    return


def activate_profile_service(max_bytes: int = 10 * 1024 * 1024, backup_count: int = 10):

    # Guard against attempts to activate more than one, activation profile.
    if RuntimeVariables.AM_ACTIVATION_PROFILE is not None:
        errmsg = "An attempt was made to activate multiple environment activation profiles. profile={}".format(
            RuntimeVariables.AM_ACTIVATION_PROFILE
        )
        raise SemanticError(errmsg)

    this_app = ThisApplicationSingleton()

    this_app.override_variable_value(RuntimeVariablesDesc.AM_ACTIVATION_PROFILE, ActivationProfile.Service)

    service_name = this_app.service_name
    if service_name is None:
        errmsg = "The 'service_name' needs to be set on when you call 'establish_app_persona'."
        raise SemanticError(errmsg)

    this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_LEVEL_CONSOLE, LogLevel.INFO)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY, os.path.join(this_app.presence_dir, "services", service_name))

    _activate_profile_common(this_app)

    log_directory = RuntimeVariables.AM_LOG_DIRECTORY
    log_basename = RuntimeVariables.AM_LOG_BASENAME

    logging_location = LoggingLocation(log_directory, log_basename)

    console_level = RuntimeVariables.AM_LOG_LEVEL_CONSOLE
    file_level = RuntimeVariables.AM_LOG_LEVEL_FILE

    activate_service_logging(logging_location, console_level, file_level, max_bytes, backup_count)

    return


def activate_profile_job(job_type: JobType):
    
    # Guard against attemps to activate more than one, activation profile.
    if RuntimeVariables.AM_ACTIVATION_PROFILE is not None:
        errmsg = "An attempt was made to activate multiple environment activation profiles. profile={}".format(
            RuntimeVariables.AM_ACTIVATION_PROFILE
        )
        raise RuntimeError(errmsg)

    this_app = ThisApplicationSingleton()
    this_app.override_variable_value(RuntimeVariablesDesc.AM_ACTIVATION_PROFILE, ActivationProfile.Job)
    this_app.override_variable_value(RuntimeVariablesDesc.AM_JOB_TYPE, job_type)

    _activate_profile_common(this_app)

    this_app.override_variable_value(RuntimeVariablesDesc.AM_LOG_DIRECTORY, RuntimeVariables.AM_OUTPUT_DIRECTORY)
    
    log_directory = RuntimeVariables.AM_LOG_DIRECTORY
    log_basename = RuntimeVariables.AM_LOG_BASENAME

    logging_location = LoggingLocation(log_directory, log_basename)

    console_level = RuntimeVariables.AM_LOG_LEVEL_CONSOLE
    file_level = RuntimeVariables.AM_LOG_LEVEL_FILE

    activate_standard_file_logging(logging_location, console_level, file_level)

    return


def _activate_profile_common(this_app: ThisApplication):
    """
    """
    
    from ccai.xmodules.xdatetime import DATETIME_FORMAT_FILESYSTEM

    

    # We set all the variables for config file options from the environment
    # we just loaded, these might get overridden late but that is ok
    current_traceback_policy = RuntimeVariables.AM_DIAGNOSTICS_TRACEBACK_POLICY_OVERRIDE

    if current_traceback_policy is None and TRACEBACK_CONFIG.TRACEBACK_POLICY_OVERRIDE is not None:
        if TRACEBACK_CONFIG.TRACEBACK_POLICY_OVERRIDE not in VALID_MEMBER_TRACE_POLICY:
            errmsg = "Invalid traceback policy environment value. TRACEBACK_POLICY_OVERRIDE={}".format(
                TRACEBACK_CONFIG.TRACEBACK_POLICY_OVERRIDE
            )
            raise ConfigurationError(errmsg)

    jobtype = RuntimeVariables.AM_JOB_TYPE
    starttime_name = RuntimeVariables.AM_STARTTIME.strftime(DATETIME_FORMAT_FILESYSTEM)

    fill_dict = {
        "starttime": starttime_name
    }

    job_output_directory = None
    if RuntimeVariables.AM_JOB_ID is None or RuntimeVariables.AM_JOB_ID == DefaultValue.NotSet:
        this_app.override_variable_value(RuntimeVariablesDesc.AM_JOB_ID, str(uuid.uuid4()))

    # We want to pull the console and testresults value from the configuration, because if its not there it
    # will be set from the default_dir_template variable
    #ctx.insert(ContextPaths.STARTTIME, RuntimeVariables.AM_STARTTIME)
    #ctx.insert(ContextPaths.JOB_ID, RuntimeVariables.AM_JOB_ID)

    # Figure out which output directory to set as the current process output directory.  The output directory
    # determines where loggin will go and is different depending on the activation mode of the test framework
    presence_dir = RuntimeVariables.AM_PRESENCE_DIR

    if jobtype == JobType.Infrastructure:
        default_dir_template = os.path.join(presence_dir, "results", "infrastructure", "%(starttime)s")
        outdir_template = default_dir_template
        job_output_directory = outdir_template % fill_dict
        this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_INFRASTRUCTURE, job_output_directory)

    elif jobtype == JobType.Orchestration:
        default_dir_template = os.path.join(presence_dir, "results", "orchestration", "%(starttime)s")
        outdir_template = RuntimeVariables.AM_TEMPLATE_PATH_FOR_ORCHESTRATION
        if outdir_template is None:
            outdir_template = default_dir_template
        job_output_directory = outdir_template % fill_dict
        this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_ORCHESTRATION, job_output_directory)

    elif jobtype == JobType.Build:
        default_dir_template = os.path.join(presence_dir, "results", "build", "%(starttime)s")
        outdir_template = RuntimeVariables.AM_TEMPLATE_PATH_FOR_BUILD
        if outdir_template is None:
            outdir_template = default_dir_template
        job_output_directory = outdir_template % fill_dict
        this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_BUILD, job_output_directory)

    elif jobtype == JobType.TestRun:
        if RuntimeVariables.AM_OUTPUT_DIRECTORY is None:
            default_dir_template = os.path.join(presence_dir, "results", "testresults", "%(starttime)s")
            outdir_template = RuntimeVariables.AM_TEMPLATE_PATH_FOR_TESTS
            if outdir_template is None:
                outdir_template = default_dir_template
            job_output_directory = outdir_template % fill_dict
            this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_TESTS, job_output_directory)

        else:
            job_output_directory = RuntimeVariables.AM_OUTPUT_DIRECTORY % fill_dict
            this_app.override_variable_value(RuntimeVariablesDesc.AM_RESULT_PATH_FOR_TESTS, job_output_directory)

    else:
        job_output_directory = os.getcwd()

    # If output directory was not already set, use the output directory for jobs
    if RuntimeVariables.AM_OUTPUT_DIRECTORY is None:
        this_app.override_variable_value(RuntimeVariablesDesc.AM_OUTPUT_DIRECTORY, job_output_directory)

    return

