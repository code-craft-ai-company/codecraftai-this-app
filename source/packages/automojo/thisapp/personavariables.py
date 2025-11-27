
from automojo.thisapp.appvardesc import AppVarDesc
from automojo.thisapp.contextpaths import PersonaContextPaths

class PersonaVariableDesc:

    AM_NAME = AppVarDesc(context_path=PersonaContextPaths.PRESENCE_NAME)
    AM_LOGGER_NAME = AppVarDesc()
    AM_LOG_BASENAME = AppVarDesc()
    AM_LOG_DIRECTORY = AppVarDesc()
    
    AM_PRESENCE_DIRECTORY = AppVarDesc(context_path=PersonaContextPaths.PRESENCE_HOME_DIRECTORY)
    
    AM_SETTINGS_FILE = AppVarDesc()

    AM_EXTENSION_MODULES = AppVarDesc(context_path=PersonaContextPaths.PRESENCE_EXTENSIONS)
    AM_SERVICE_NAME = AppVarDesc()
