"""
.. module:: personavariables
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that defines persona-related application variable declarations and accessors.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from automojo.thisapp.appvardesc import AppVarDesc, VariableSource
from automojo.thisapp.appvarset import AppVarSet
from automojo.thisapp.appvaraccessor import AppVarAccessor
from automojo.thisapp.contextpaths import ContextPaths

class PersonaVariablesDesc(AppVarSet):

    AM_NAME = AppVarDesc(source=VariableSource.NONE, context_path=ContextPaths.PRESENCE_NAME)

    AM_LOGGER_NAME = AppVarDesc(source=VariableSource.NONE)
    AM_LOG_BASENAME = AppVarDesc(source=VariableSource.NONE)
    AM_PRESENCE_DIR = AppVarDesc(source=VariableSource.NONE, context_path=ContextPaths.PRESENCE_HOME_DIRECTORY)
    AM_LOG_DIRECTORY = AppVarDesc(source=VariableSource.NONE)
    
    AM_SETTINGS_FILENAME = AppVarDesc(source=VariableSource.NONE)
    
    AM_EXTENSIONS = AppVarDesc(source=VariableSource.NONE, context_path=ContextPaths.PRESENCE_EXTENSIONS)
    AM_SERVICE_NAME = AppVarDesc(source=VariableSource.NONE)



class PersonaVariables:

    AM_NAME = AppVarAccessor(PersonaVariablesDesc.AM_NAME)

    AM_LOGGER_NAME = AppVarAccessor(PersonaVariablesDesc.AM_LOGGER_NAME)
    AM_LOG_BASENAME = AppVarAccessor(PersonaVariablesDesc.AM_LOG_BASENAME)
    AM_PRESENCE_DIR = AppVarAccessor(PersonaVariablesDesc.AM_PRESENCE_DIR)
    AM_LOG_DIRECTORY = AppVarAccessor(PersonaVariablesDesc.AM_LOG_DIRECTORY)
    
    AM_SETTINGS_FILENAME = AppVarAccessor(PersonaVariablesDesc.AM_SETTINGS_FILENAME)
    
    AM_EXTENSIONS = AppVarAccessor(PersonaVariablesDesc.AM_EXTENSIONS)
    AM_SERVICE_NAME = AppVarAccessor(PersonaVariablesDesc.AM_SERVICE_NAME)
