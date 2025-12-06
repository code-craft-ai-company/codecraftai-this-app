
from typing import List

from automojo.thisapp.appvardesc import AppVarDesc

class AppVarSet:
    """
        Class that serves as a base class for variable declaration classes. 
    """

    @classmethod
    def items(cls) -> List["AppVarSet"]:
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