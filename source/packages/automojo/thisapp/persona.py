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

from automojo.errors.exceptions import SemanticError

from automojo.thisapp.thisapplication import ThisApplication, ContextInsertCallable
from automojo.thisapp.personavariables import PersonaVariablesDesc

EXTENSION_MODULES_SEP = ";"

class AppPersona:

    AM_NAME = None
    AM_LOGGER_NAME = None
    AM_LOG_BASENAME = None
    AM_PRESENCE_DIR = None
    AM_LOG_DIRECTORY = None
    AM_SETTINGS_FILENAME = None
    
    AM_EXTENSIONS = None
    AM_SERVICE_NAME = None


APP_PERSONA_ESTABLISHED = False

def establish_app_persona(*, name: str, logger_name: str, log_basename: str, presence_dir: Optional[str]=None,
                          log_directory: Optional[str]=None, settings_file: Optional[str]=None,
                          extensions: Optional[str]=None, service_name: Optional[str]=None,
                          context_insert: Optional[ContextInsertCallable]=None, **other):
    
    global APP_PERSONA_ESTABLISHED

    if not APP_PERSONA_ESTABLISHED:
        APP_PERSONA_ESTABLISHED = True
    
        AppPersona.AM_NAME = name
        AppPersona.AM_LOGGER_NAME = logger_name
        AppPersona.AM_LOG_BASENAME = log_basename

        if presence_dir is not None:
            AppPersona.AM_PRESENCE_DIR = presence_dir
        else:
            AppPersona.AM_PRESENCE_DIR = os.path.join("~", name.lower())

        if log_directory is not None:
            AppPersona.AM_LOG_DIRECTORY = log_directory
        else:
            AppPersona.AM_LOG_DIRECTORY = os.path.join(AppPersona.AM_PRESENCE_DIR, "logs")
        
        if settings_file is not None:
            # If we are only given the filename, the file must be located in the presence directory
            if os.path.basename(settings_file) == settings_file:
                AppPersona.AM_SETTINGS_FILENAME = os.path.join(AppPersona.AM_PRESENCE_DIR, settings_file)
            else:
                AppPersona.AM_SETTINGS_FILENAME = os.path.abspath(os.path.expandvars(os.path.expanduser(settings_file)))
        else:
            AppPersona.AM_SETTINGS_FILENAME = os.path.join(AppPersona.AM_PRESENCE_DIR, 'settings.config')

        AppPersona.AM_EXTENSIONS = extensions
        AppPersona.AM_SERVICE_NAME = service_name
        
        from automojo.thisapp import wellknown

        if wellknown.THISAPPLICATION_SINGLETON is not None:
            errmsg = "The singleton 'wellknown.THISAPPLICATION_SINGLETON' must not be set when calling 'establish_app_persona'"
            raise SemanticError(errmsg)
        
        this_app = ThisApplication(name=name, logger_name=logger_name, log_basename=log_basename, presence_dir=AppPersona.AM_PRESENCE_DIR,
                                   log_directory=AppPersona.AM_LOG_DIRECTORY, settings_file=AppPersona.AM_SETTINGS_FILENAME,
                                   extensions=AppPersona.AM_EXTENSIONS, service_name=AppPersona.AM_SERVICE_NAME,
                                   context_insert=context_insert, from_establish_app_persona=True)

        wellknown.SINGLETON_LOCK.acquire()
        try:
            wellknown.THISAPPLICATION_SINGLETON = this_app
        finally:
            wellknown.SINGLETON_LOCK.release()

        this_app.override_variable_value(PersonaVariablesDesc.AM_NAME, this_app.name)
        this_app.override_variable_value(PersonaVariablesDesc.AM_LOGGER_NAME, AppPersona.AM_LOGGER_NAME)
        this_app.override_variable_value(PersonaVariablesDesc.AM_LOG_BASENAME, AppPersona.AM_LOG_BASENAME)
        this_app.override_variable_value(PersonaVariablesDesc.AM_LOG_DIRECTORY, AppPersona.AM_LOG_DIRECTORY)
        this_app.override_variable_value(PersonaVariablesDesc.AM_PRESENCE_DIR, AppPersona.AM_PRESENCE_DIR)
        this_app.override_variable_value(PersonaVariablesDesc.AM_SERVICE_NAME, AppPersona.AM_SERVICE_NAME)
        this_app.override_variable_value(PersonaVariablesDesc.AM_EXTENSIONS, AppPersona.AM_EXTENSIONS)        

    return