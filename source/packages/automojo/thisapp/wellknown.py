"""
.. module:: wellknown
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that provides a wellknow startup configuration singleton.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import logging
import threading

from automojo.errors.exceptions import SemanticError

from automojo.extension.constants import EXT_MOD_SEP
from automojo.extension.factory.superfactory import SuperFactory

from automojo.thisapp.thisapplication import ThisApplication
from automojo.thisapp.personavariables import PersonaVariablesDesc

# NOTE: This code is loaded super early where there is likely to only be a single thread
#       so there is likely no need for any locking.


THISAPPLICATION_SINGLETON = None
CONFIGURED_SUPER_FACTORY = None

SINGLETON_LOCK = threading.RLock()


def ThisApplicationSingleton() -> ThisApplication:
    """
        The `ThisApplicationSingleton` function returns a singleton instance of the `ThisApplication` object.
        The `ThisApplication` sets up a persistant presence for the storage of configuration files on a host
        machine, helps to manage configuration settings, and provides dedicated input resolution (setting, environment,
        parameter).
        
        :return: A singleton instance of the `ThisApplication`.
    """

    global THISAPPLICATION_SINGLETON

    SINGLETON_LOCK.acquire()
    try:
        if THISAPPLICATION_SINGLETON is None:

            errmsg = "You must call '' early in your application startup to define your application's presence" \
                     " settings before attempting to use the `ThisApplication` object or its corresponding singleton."
            raise SemanticError(errmsg)

    finally:
        SINGLETON_LOCK.release()

    return THISAPPLICATION_SINGLETON

def ConfiguredSuperFactorySingleton():

    global CONFIGURED_SUPER_FACTORY

    SINGLETON_LOCK.acquire()
    try:
        if CONFIGURED_SUPER_FACTORY is None:
            extension_modules = []

            from automojo.thisapp import persona

            if not persona.APP_PERSONA_ESTABLISHED:
                warnmsg = "IMPORTANT!!! You should establish application presence settings by calling " \
                          "`establish_presence_settings` before attempting to use the extensibility superfactory singleton."
                logger = logging.getLogger()
                logger.warn(warnmsg)

            this_app = ThisApplicationSingleton()

            extension_modules_value: str = this_app.get_variable_value(PersonaVariablesDesc.AM_EXTENSIONS)
            
            if extension_modules_value is not None and len(extension_modules_value) > 0:
                extension_modules_value.strip()
                extension_modules = extension_modules_value.split(EXT_MOD_SEP)
            
            CONFIGURED_SUPER_FACTORY = SuperFactory(extension_modules)
    finally:
        SINGLETON_LOCK.release()

    return CONFIGURED_SUPER_FACTORY