

from automojo.thisapp.appvardesc import AppVarDesc, VariableSource
from automojo.thisapp.appvaraccessor import AppVarAccessor


class PersonaVariablesDesc:

    AP_NAME = AppVarDesc(source=VariableSource.NONE)

    AP_LOGGER_NAME = AppVarDesc(source=VariableSource.NONE)
    AP_LOG_BASENAME = AppVarDesc(source=VariableSource.NONE)
    AP_PRESENCE_DIR = AppVarDesc(source=VariableSource.NONE)
    AP_LOG_DIRECTORY = AppVarDesc(source=VariableSource.NONE)
    
    AP_SETTINGS_FILENAME = AppVarDesc(source=VariableSource.NONE)
    
    AP_EXTENSIONS = AppVarDesc(source=VariableSource.NONE)
    AP_SERVICE_NAME = AppVarDesc(source=VariableSource.NONE)



class PersonaVariables:

    AP_NAME = AppVarAccessor(PersonaVariablesDesc.AP_NAME)

    AP_LOGGER_NAME = AppVarAccessor(PersonaVariablesDesc.AP_LOGGER_NAME)
    AP_LOG_BASENAME = AppVarAccessor(PersonaVariablesDesc.AP_LOG_BASENAME)
    AP_PRESENCE_DIR = AppVarAccessor(PersonaVariablesDesc.AP_PRESENCE_DIR)
    AP_LOG_DIRECTORY = AppVarAccessor(PersonaVariablesDesc.AP_LOG_DIRECTORY)
    
    AP_SETTINGS_FILENAME = AppVarAccessor(PersonaVariablesDesc.AP_SETTINGS_FILENAME)
    
    AP_EXTENSIONS = AppVarAccessor(PersonaVariablesDesc.AP_EXTENSIONS)
    AP_SERVICE_NAME = AppVarAccessor(PersonaVariablesDesc.AP_SERVICE_NAME)
