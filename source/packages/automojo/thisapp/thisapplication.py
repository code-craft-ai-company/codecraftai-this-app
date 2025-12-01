"""
.. module:: thisapplication
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that containing the `ThisApplication` object.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Callable, Optional, Union

import os

from configparser import ConfigParser

from automojo.errors.exceptions import SemanticError

from automojo.thisapp.appvardesc import AppVarDesc, VariableSource, ValueConverter
from automojo.thisapp.appvarset import AppVarSet

ContextInsertCallable = Callable[[str, Any], Any]

class ThisApplication:
    """
        Represents a single point of service for interacting with the application presence.
    """

    def __init__(self, *, name: str, logger_name: str, log_basename: str, presence_dir: str, log_directory: str,
                 settings_file: str, extensions: str, service_name: str, context_insert: ContextInsertCallable, **other):
        """
            Constructs an `ThisApplication` object.

            :param name: A one-word short name for the application.
            :param presence_dir: The directory that will represent the settings, configuration, and data storage
                                 presence for the application.
            :param settings_file: The path to the settings file that stores the application default settings.
            :param extension_modules: A 
        """

        if "from_establish_app_persona" not in other:
            errmsg = "The `ThisApplication` singleton object should not be instantiated directly. Call `establish_app_persona` " \
                     "to establish application wide presence settings and then use the wellknown singlton to access the application presence" \
                     "instance."
            raise SemanticError(errmsg)

        self._name = name
        self._presence_dir = presence_dir
        self._settings_file = settings_file
        self._extensions = extensions
        self._logger_name = logger_name
        self._log_basename = log_basename
        self._log_directory = log_directory
        self._service_name = service_name


        self._config_parser = ConfigParser()
        if os.path.exists(self._settings_file):
            self._config_parser.read(self._settings_file)

        self._context_insert =context_insert

        self._startup_variables = {}
        self._startup_variables.update(os.environ)

        self._resolved_variables = {}

        self._application_variables = {}

        return
    
    @property
    def name(self):
        return self._name
    
    @property
    def presence_dir(self):
        return self._presence_dir
    
    @property
    def settings_file(self):
        return self._settings_file
    
    @property
    def extensions(self):
        return self._extensions
    
    @property
    def logger_name(self):
        return self._logger_name
    
    @property
    def log_basename(self):
        return self._log_basename
    
    @property
    def log_directory(self):
        return self._log_directory
    
    @property
    def service_name(self):
        return self._service_name


    def get_variable_value(self, variable_desc: AppVarDesc, default: Optional[str]=None, converter: Optional[ValueConverter] = None) -> Union[str, Any]:
        """
            Gets the value of an application variable using the settings order of precedence.  The order of presence is:
              - If the variable value has been overridden at the application level, use the override value
              - If an environment variable is found, use the environment value
              - If a value is specified in the settings file, use the settings value
              - Else use the value passed as the default parameter to this method..

            :param variable_desc: A description of the variable being retrieved.
            :param default: The default value to return if the variable is not found.
            :param converter: A lamba expression of function that will convert the str value to a consumable python type.

            :returns: A str value or type if a converter was passed.

            ..note:: The values being input as the default should be in string format.  The value coming out of this function will be a string unless
                     a `converter` parameter is provided. 
        """

        vkey = variable_desc.key
        vname = variable_desc.name

        if vkey not in self._application_variables:

            default_found = None
            if default is not None:
                default_found = default
            elif variable_desc.default is not None:
                default_found = variable_desc.default

            sname = variable_desc.section

            if variable_desc.source & VariableSource.ENVIRONMENT and  vname in os.environ:
                vval = os.environ[vname]
            elif variable_desc.source & VariableSource.SETTINGS and sname in self._config_parser:
                conf_section = self._config_parser[sname]
                vval = conf_section[vname]
            else:
                vval = default_found

            self._application_variables[vkey] = vval

        else:
            vval = self._application_variables[vkey]

        if converter is not None and vval is not None:
            vval = converter(vval)

        return vval


    def override_variable_value(self, variable_desc: AppVarDesc, new_value: Any):
        """
            Used to override an application level variable because an input parameter with higher precedence to the settings file
            environment variable was passed.  For example, an input parameter on the commandline that was associated with
            the variable.

            :param variable_desc: TA description of the variable being overridden.
            :param new_value: The new value to assign to the application variable.
        """

        vkey = variable_desc.key
        vname = variable_desc.name
        
        self._application_variables[vkey] = new_value
        
        if variable_desc.source & VariableSource.ENVIRONMENT and variable_desc.overrides:
            envval = new_value
            if not isinstance(new_value, str):
                envval = str(new_value)
            os.environ[vname] = envval
        
        if self._context_insert is not None and variable_desc.context_path is not None:
            self._context_insert(variable_desc.context_path, new_value)

        return


    def resolve_variable_set(self, variable_set: AppVarSet):
        """
            Resolve the variables that are attached to the `AppVarSet` being passed.

            :param variable_set: A variable set that has variables attached that should be resolved.
        """

        variable_items = variable_set.items()

        for vdesc in variable_items:
            vkey = vdesc.key

            # Only resolve variables that haven't already been resolved
            if vkey not in self._resolved_variables:
                self._perform_variable_resolution(vdesc)
                self._resolved_variables[vkey] = True

        return

    def _perform_variable_resolution(self, var_desc: AppVarDesc):
        """
            To resolve the variable, we get its value and then store the result into the context
            if we have a path for the variable.
        """

        # If the variable has not been resolved, get its value to force it
        # to be loaded into the cache.  
        vval = self.get_variable_value(var_desc)
        
        # If the variable has a designated context location, store the variable
        if self._context_insert is not None and var_desc.context_path is not None:
            self._context_insert(var_desc.context_path, vval)

        return