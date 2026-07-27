"""
.. module:: persona
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: The settings in this module help to establish the persona of the application, it
               lets applications say who they are and where they want to live on the host.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Optional

import os

from ccai.errors.exceptions import SemanticError

from ccai.thisapp.thisapplication import ThisApplication
from ccai.thisapp.personavariables import PersonaVariablesDesc

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
                          extensions: Optional[str]=None, service_name: Optional[str]=None, **other):
    
    global APP_PERSONA_ESTABLISHED

    if len(other) > 0:
        # A misnamed keyword must not pass silently: 'home_dir' instead of
        # 'presence_dir' or 'extension_modules' instead of 'extensions' would
        # be swallowed here, and the application would run with a DEFAULT it
        # never chose (results under a literal '~/' directory in the CWD,
        # extensions that never load).
        unknown = ", ".join(sorted(other.keys()))
        errmsg = "establish_app_persona was passed unrecognized keyword arguments: {}".format(unknown)
        raise SemanticError(errmsg)

    if not APP_PERSONA_ESTABLISHED:
        APP_PERSONA_ESTABLISHED = True

        AppPersona.AM_NAME = name
        AppPersona.AM_LOGGER_NAME = logger_name
        AppPersona.AM_LOG_BASENAME = log_basename

        if presence_dir is not None:
            AppPersona.AM_PRESENCE_DIR = presence_dir
        else:
            AppPersona.AM_PRESENCE_DIR = os.path.join("~", name.lower())

        # Expand '~' and environment variables and anchor to an absolute path.
        # Without this, the default above is the RELATIVE path '~/<name>', and
        # every path derived from the presence directory silently lands under
        # a literal '~/' directory inside the current working directory.
        AppPersona.AM_PRESENCE_DIR = os.path.abspath(os.path.expandvars(os.path.expanduser(AppPersona.AM_PRESENCE_DIR)))

        if log_directory is not None:
            AppPersona.AM_LOG_DIRECTORY = os.path.abspath(os.path.expandvars(os.path.expanduser(log_directory)))
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
        
        from ccai.thisapp import wellknown

        if wellknown.THISAPPLICATION_SINGLETON is not None:
            errmsg = "The singleton 'wellknown.THISAPPLICATION_SINGLETON' must not be set when calling 'establish_app_persona'"
            raise SemanticError(errmsg)
        
        this_app = ThisApplication(name=name, logger_name=logger_name, log_basename=log_basename, presence_dir=AppPersona.AM_PRESENCE_DIR,
                                   log_directory=AppPersona.AM_LOG_DIRECTORY, settings_file=AppPersona.AM_SETTINGS_FILENAME,
                                   extensions=AppPersona.AM_EXTENSIONS, service_name=AppPersona.AM_SERVICE_NAME,
                                   from_establish_app_persona=True)

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

def reset_app_persona() -> None:
    """
        Reset the application persona so another one can be established.

        Establishing a persona is a once-per-process operation: `AppPersona`
        holds its settings as class attributes and `wellknown` holds the single
        application instance built from them. A test process that needs to
        establish a second persona — or a test suite whose collection imports
        two application modules — has no way past that without this.

        Everything `establish_app_persona` sets is cleared, including the
        configured super factory: it is built from the persona's extension
        modules, so leaving it in place would hand the next persona the
        previous one's extensions.

        .. warning::
            For tests only. Resetting a live application's persona leaves any
            code already holding the old instance pointing at a discarded one.

        :returns: ``None``
    """
    global APP_PERSONA_ESTABLISHED

    # Imported here rather than at module scope, matching
    # establish_app_persona: wellknown imports back from this tier.
    from ccai.thisapp import wellknown

    wellknown.SINGLETON_LOCK.acquire()
    try:
        APP_PERSONA_ESTABLISHED = False

        wellknown.THISAPPLICATION_SINGLETON = None
        wellknown.CONFIGURED_SUPER_FACTORY = None

        AppPersona.AM_NAME = None
        AppPersona.AM_LOGGER_NAME = None
        AppPersona.AM_LOG_BASENAME = None
        AppPersona.AM_PRESENCE_DIR = None
        AppPersona.AM_LOG_DIRECTORY = None
        AppPersona.AM_SETTINGS_FILENAME = None
        AppPersona.AM_EXTENSIONS = None
        AppPersona.AM_SERVICE_NAME = None
    finally:
        wellknown.SINGLETON_LOCK.release()

    return
