"""Auxiliary functions for translation."""
import importlib
from typing import Callable


def _import_function_by_string(module_function_string: str) -> Callable:
    """Import a callable or class from a dotted path string.

    Args:
        module_function_string (str):
            Dotted path in the form ``package.module.Attribute``.

    Returns:
        Callable:
            Attribute imported from the module.

    Raises:
        ModuleNotFoundError:
            If the module cannot be imported.
        AttributeError:
            If the attribute does not exist on the module.
    """
    # Split the module and function names
    module_name, function_name = module_function_string.rsplit('.', 1)
    # Import the module
    module = importlib.import_module(module_name)
    # Retrieve the function
    func = getattr(module, function_name)
    return func
