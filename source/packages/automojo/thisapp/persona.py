"""
.. module:: constants
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The settings in this module help to establish the persona of the application, it
               lets applications say who they are and where they want to live on the host.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Optional

import os

from enum import Enum

from automojo.errors.exceptions import SemanticError


EXTENSION_MODULES_SEP = ";"

class AppPersona:

    AP_NAME = None
    AP_LOGGER_NAME = None
    AP_LOG_BASENAME = None
    AP_PRESENCE_DIR = None
    AP_LOG_DIRECTORY = None
    AP_SETTINGS_FILENAME = None
    
    AP_EXTENSIONS = None
    AP_SERVICE_NAME = None


class PersonaContextPaths(str, Enum):

    PRESENCE_NAME = "/environment/presence/name"
    PRESENCE_HOME_DIRECTORY = "/environment/presence/home"
    PRESENCE_EXTENSIONS = "/environment/presence/extensions"


def establish_app_persona(*, name: str, logger_name: str, log_basename: str, presence_dir: Optional[str]=None,
                          log_directory: Optional[str]=None, settings_file: Optional[str]=None,
                          extensions: Optional[str]=None, service_name: Optional[str]=None, **other):
    
    AppPersona.AP_NAME = name
    AppPersona.AP_LOGGER_NAME = logger_name
    AppPersona.AP_LOG_BASENAME = log_basename

    if presence_dir is not None:
        AppPersona.AP_PRESENCE_DIR = presence_dir
    else:
        AppPersona.AP_PRESENCE_DIR = os.path.join("~", name.lower())

    if log_directory is not None:
        AppPersona.AP_LOG_DIRECTORY = log_directory
    else:
        AppPersona.AP_LOG_DIRECTORY = os.path.join(AppPersona.AP_PRESENCE_DIR, "logs")
    
    if settings_file is not None:
        # If we are only given the filename, the file must be located in the presence directory
        if os.path.basename(settings_file) == settings_file:
            AppPersona.AP_SETTINGS_FILENAME = os.path.join(AppPersona.AP_PRESENCE_DIR, settings_file)
        else:
            AppPersona.AP_SETTINGS_FILENAME = os.path.abspath(os.path.expandvars(os.path.expanduser(settings_file)))
    else:
        AppPersona.AP_SETTINGS_FILENAME = os.path.join(AppPersona.AP_PRESENCE_DIR, 'settings.config')

    AppPersona.AP_EXTENSIONS = extensions
    AppPersona.AP_SERVICE_NAME = service_name
    
    from automojo.thisapp.thisapplication import ThisApplication
    from automojo.thisapp import wellknown

    if wellknown.THISAPPLICATION_SINGLETON is not None:
        errmsg = "The singleton 'wellknown.THISAPPLICATION_SINGLETON' must not be set when calling 'establish_app_persona'"
        raise SemanticError(errmsg)
    
    this_app = ThisApplication(name=name, logger_name=logger_name, log_basename=log_basename,
                               log_directory=AppPersona.AP_LOG_DIRECTORY)

    wellknown.SINGLETON_LOCK.acquire()
    try:
        wellknown.THISAPPLICATION_SINGLETON = this_app
    finally:
        wellknown.SINGLETON_LOCK.release()

    return