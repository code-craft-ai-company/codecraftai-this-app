"""
.. module:: wellknown
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that provides a wellknow startup configuration singleton.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

import threading

from automojo.errors.exceptions import SemanticError

from automojo.thisapp.thisapplication import ThisApplication

# NOTE: This code is loaded super early where there is likely to only be a single thread
#       so there is likely no need for any locking.


THISAPPLICATION_SINGLETON = None

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

