
from enum import Enum

class PersonaContextPaths(str, Enum):

    PRESENCE_NAME = "/environment/presence/name"
    PRESENCE_HOME_DIRECTORY = "/environment/presence/home"
    PRESENCE_EXTENSIONS = "/environment/presence/extensions"

