import importlib
import sys
from typing import Any

# 1. Define the mapping: "accessing .ext" -> "imports my_framework_ext"
_EXTENSION_MAP = {
    "ext": "my_framework_ext",
}

# 2. PEP 562: __getattr__ is called only if the attribute isn't found normally
def __getattr__(name: str) -> Any:
    if name in _EXTENSION_MAP:
        package_name = _EXTENSION_MAP[name]
        try:
            print(f"... Lazily importing '{package_name}' for namespace '{name}' ...")
            module = importlib.import_module(package_name)
            return module
        except ImportError as e:
            raise ImportError(
                f"Missing extension! To use 'my_framework.{name}', "
                f"please install '{package_name}'."
            ) from e
            
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# 3. Optional: Help IDEs / Autocomplete know this attribute exists
#    (Runtime doesn't need this, but Type Checkers do)
if False:
    from my_framework_ext import *
