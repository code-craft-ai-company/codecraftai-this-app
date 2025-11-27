
from typing import Any, Callable, Optional, Protocol, Union

import enum
import re

REGEX_ENVIRONMENT_VARIABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
INVALID_SECTION_NAME_CHARACTERS = ['[', ']', '\n', '\r', '\t', '\x00']


def assert_section_name(section_name: str) -> str:
    """
        Asserts that the section name provided is a valid configuration file section name.

        :param section_name: The section name to validate.

        :raises: AssertionError if the provided 'section_name' is not in a valid name format.
    """
    if not isinstance(section_name, str):
        errmsg = "The parameter 'section_name' must be a string."
        raise AssertionError(errmsg)

    stripped_section_name = section_name.strip()
    if len(stripped_section_name) == 0:
        errmsg = "The parameter 'section_name' must not be empty or only whitespace."
        raise AssertionError(errmsg)

    if stripped_section_name != section_name:
        errmsg = "The parameter 'section_name' must not contain leading or trailing whitespace."
        raise AssertionError(errmsg)

    for invalid_char in INVALID_SECTION_NAME_CHARACTERS:
        if invalid_char in section_name:
            errmsg = (
                f"The parameter 'section_name' contains an invalid character "
                f"'{invalid_char}'. section_name='{section_name}'"
            )
            raise AssertionError(errmsg)

    return section_name


def assert_variable_name(var_name: str) -> str:
    """
        Asserts that the variable name provided can be used as an environment variable name and
        configuration file variable name.

        :param var_name: The variable name to validate.

        :raises: AssertionError if the provided 'var_name' is not in a valid name format.
    """
    if not isinstance(var_name, str):
        errmsg = "The parameter 'var_name' must be a string."
        raise AssertionError(errmsg)

    if len(var_name) == 0:
        errmsg = "The parameter 'var_name' must not be empty."
        raise AssertionError(errmsg)

    if not REGEX_ENVIRONMENT_VARIABLE_NAME.match(var_name):
        errmsg = (
            "The parameter 'var_name' must be a valid environment variable name and "
            "configuration file option name. Names must start with a letter or underscore and "
            "contain only alphanumeric characters or underscores."
        )
        raise AssertionError(errmsg)

    return var_name


ValueConverter = Callable[[str], Any]

class VariableSource(enum.Flag):
    NONE = 0
    ENVIRONMENT = 1
    SETTINGS = 2
    BOTH = 3


class AppVarDesc:
    """
        Describes an application variable that is loaded from the settings file or from the environment variables
    """

    def __init__(self, *, section: str='DEFAULT', default: str=None, overrides: bool=True, context_path: Optional[str]=None,
                 source: VariableSource=VariableSource.BOTH, converter: Optional[ValueConverter]=None):
        self._section = assert_section_name(section)
        self._default = default
        self._overrides = overrides
        self._context_path = context_path
        self._source = source
        self._converter = converter
    
        self._name = None
        self._key = None
        self._owner = None
        return
    
    @property
    def context_path(self) -> Union[str, None]:
        """
            The path that should be used to store this variable in the context.
        """
        return self._context_path

    @property
    def converter(self) -> Union[ValueConverter, None]:
        return self._converter

    @property
    def default(self) -> Union[str, None]:
        """
            The default value associated with this variable or None if no default was provided.
        """
        return self._default

    @property
    def key(self) -> str:
        """
            The key to use when storing and retrieving the variable description.
        """
        return self._key

    @property
    def name(self) -> str:
        """
            The name associated with this variable
        """
        return self._name
    
    @property
    def overrides(self) -> str:
        """
            Indicates this variable should override its corresponding OS environment variable.
        """
        return self._overrides

    @property
    def section(self) -> str:
        """
            The configuration file section to look for this variable in.
        """
        return self._section
    
    @property
    def source(self) -> VariableSource:
        """
            A flags `VariableSource` flags value that indicates which sources can be used for this variable. 
        """
        return self._source

    def __set_name__(self, owner: type, name: str) -> None:
        """
            Captures the class and attribute name this reader is bound to.
        """
        
        assert_variable_name(name)

        self._owner = owner
        self._name = name

        self._key = f"{self._section}->{self._name}"

        return

    def __repr__(self):
        rval = f"AppVarDesc(name='{self._name}', section='{self._section}')"
        return rval

    def __str__(self):
        return self._name

