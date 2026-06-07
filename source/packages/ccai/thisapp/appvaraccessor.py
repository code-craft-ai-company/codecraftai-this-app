"""
.. module:: appvaraccessor
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module that provides the variable accessor descriptor and base class for
               variable declaration containers.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []

from typing import Any, List, Optional

from ccai.thisapp.appvardesc import AppVarDesc, assert_variable_name

class AppVarAccessor:
    """
        Class that establishes a way to declaratively read variables from the global
        ThisApplication variable storage.  The AppVarAccessor allows for convenient
        grouping of variables allowing easy access to application variables, while at
        the same time enforcing rules around how variable values are overriden.
    """

    _this_app = None

    def __init__(self, var_desc: AppVarDesc):
        """
            Initializes a variable reader descriptor that operates on a :class:`VariableDesc`.

            :param var_desc: The :class:`VariableDesc` describing the variable being read.
            :param converter: Optional callable used to convert string values before returning them.
        """
        if not isinstance(var_desc, AppVarDesc):
            errmsg = "The parameter 'var_desc' must be an instance of VariableDesc."
            raise AssertionError(errmsg)

        self._var_desc = var_desc

        self._owner: Optional[type] = None

        return

    @property
    def this_app(self):
        this_type = type(self)
        if this_type._this_app is None:
            from ccai.thisapp.wellknown import ThisApplicationSingleton
            this_type._this_app = ThisApplicationSingleton()
        return self._this_app


    def __set_name__(self, owner: type, name: str) -> None:
        """
            Captures the class and attribute name this reader is bound to.
        """
        self._owner = owner

        assert_variable_name(name)
        
        if self._var_desc.name != name:
            errmsg = (
                f"VariableDesc name '{self._var_desc.name}' does not match attribute name '{name}'."
            )
            raise AssertionError(errmsg)
        
        return

    def __call__(self, instance: Optional[object], owner: Optional[type]) -> Any:
        """
            Resolves the value for this variable by delegating to :meth:`perform_read`.
        """
        target_owner = owner if owner is not None else self._owner

        vfound = self.this_app.get_variable_value(self._var_desc)

        return vfound

    def __get__(self, instance: Optional[object], owner: Optional[type] = None) -> Any:
        """
            Supports descriptor access so referencing the attribute triggers the reader call.
        """
        return self(instance, owner)
    
    def __set__(self, instance: Optional[object], value: Any) -> None:
        """
            Prevents attempts to assign to application variables through the accessor.  Assignments
            to application variables should be made directly on ThisApplication by calling
            `this_app.override_variable_value`.  This is enforced because it makes it much simpler
            to track down 'Who' is modifying 'What' application level variables.
        """
        errmsg = f"Assignment to application level variables through the AppVarAccessor is not allowed."
        raise AttributeError(errmsg)



class VariableSet:
    """
        Class that serves as a base class for variable declaration classes. 
    """

    @classmethod
    def items(cls) -> List[AppVarDesc]:
        """
            Returns the list of 'VariableDesc' class members defined on this class and any base classes.
            The variables are returned in definition order, with values on derived classes overriding
            values from base classes that share the same attribute name.
        """
        variables_by_name = {}

        for base_cls in reversed(cls.mro()):
            if base_cls is object:
                continue

            for attr_name, attr_value in base_cls.__dict__.items():
                if isinstance(attr_value, AppVarDesc):
                    variables_by_name[attr_name] = attr_value

        rval: List[AppVarDesc] = list(variables_by_name.values())

        return rval
