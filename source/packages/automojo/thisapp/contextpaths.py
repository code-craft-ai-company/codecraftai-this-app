"""
.. module:: contextpaths
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that contains the :class:`ContextPaths` enumeration which is an enumeration
               of wellknown context paths.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from enum import Enum

class PersonaContextPaths(str, Enum):

    # ========================== environment paths ==============================    
    LOGFILE_DEBUG = "/environment/logfile_debug"
    LOGFILE_OTHER = "/environment/logfile_other"

    PRESENCE_NAME = "/environment/presence/name"
    PRESENCE_HOME_DIRECTORY = "/environment/presence/home"
    PRESENCE_EXTENSIONS = "/environment/presence/extensions"

    