# Lazy Loading Demo with PEP 562

This repository demonstrates how to use PEP 562 (`__getattr__` at module level) to implement lazy loading of extension packages in Python.

## What is PEP 562?

[PEP 562](https://www.python.org/dev/peps/pep-0562/) introduced support for `__getattr__` and `__dir__` at the module level, allowing modules to customize attribute access. This is particularly useful for:

- **Lazy loading**: Import expensive modules only when they're actually used
- **Extension packages**: Allow optional dependencies without forcing installation
- **Backward compatibility**: Provide smooth migration paths for refactored code

## Repository Structure

```text
lazy-loading-demo/
├── core/                       # Simulates the main framework repo
│   ├── pyproject.toml
│   └── src/
│       └── my_framework/
│           ├── __init__.py     # <--- The Magic (PEP 562) happens here
│           └── base.py
├── extension/                  # Simulates the extension repo
│   ├── pyproject.toml
│   └── src/
│       └── my_framework_ext/   # Distinct package name
│           ├── __init__.py
│           └── tools.py
├── meta/                       # Meta package that installs everything
│   ├── pyproject.toml
│   └── src/
│       └── my_framework_complete/
│           └── __init__.py
├── demo.py                     # The script to prove it works
└── README.md                   # This file
```

## How It Works

### The Core Package (`my_framework`)

The core package implements a `__getattr__` function at the module level in `core/src/my_framework/__init__.py`:

```python
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
```

This function is called only when an attribute isn't found through normal lookup. When you access `my_framework.ext`, Python:
1. Looks for `ext` as a regular attribute/module - not found
2. Calls `__getattr__("ext")`
3. Our code imports `my_framework_ext` and returns it
4. The import happens **only at this point**, not when `my_framework` is imported

### The Extension Package (`my_framework_ext`)

This is a completely separate, standard Python package. It doesn't know anything about the core framework and can be installed independently.

### The Meta Package (`my_framework_complete`)

This is a "catch-all" convenience package that installs both the core framework and all extensions. When you install this package, it automatically installs `my-framework` and `my-framework-ext` as dependencies. This is useful for:

- **Easy installation**: Users can install everything with a single command
- **Simplified documentation**: Just tell users to `pip install my-framework-complete`
- **Version coordination**: Ensures compatible versions of all packages are installed together

This pattern is common in Python ecosystems (e.g., `jupyter` installs multiple packages, `ansible` includes core and extensions).

## Setup Instructions

You have **two options** for installation:

### Option 1: Install the Complete Package (Recommended for Most Users)

The meta package will install both the core framework and all extensions:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# For this demo, install packages in order (in a real scenario, they'd be on PyPI):
pip install -e ./core
pip install -e ./extension
pip install -e ./meta
```

After installation, verify all packages are installed:
```bash
pip list | grep my-framework
# Should show:
# my-framework           0.1.0
# my-framework-complete  0.1.0
# my-framework-ext       0.1.0
```

### Option 2: Install Packages Individually

If you only need specific components or want to understand the lazy loading behavior:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ./core
pip install -e ./extension
```

This installs both packages separately in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling.

### 3. Run the Demo

```bash
python demo.py
```

## Expected Output

When you run the demo, you should see:

```text
1. Importing core framework...
   [Check] Is extension loaded in sys.modules? False

2. Doing core work (no extension needed)...

3. Accessing extension for the first time...
... Lazily importing 'my_framework_ext' for namespace 'ext' ...
--> LOADING: my_framework_ext (The Extension)
   [Check] Is extension loaded in sys.modules? True

4. Result: Extension logic executed!
```

### What This Proves

1. **Line 1-2**: When `my_framework` is imported, the extension is **NOT** loaded (lazy loading works!)
2. **Line 6-7**: When `my_framework.ext` is accessed, the `__getattr__` function triggers and imports the extension
3. **Line 8**: The extension's `__init__.py` prints its loading message
4. **Line 9**: After access, the extension is now in `sys.modules`
5. **Line 11**: We can use the extension's functionality

## Benefits

1. **Faster Import Times**: Core framework imports quickly; extensions load only when needed
2. **Optional Dependencies**: Extensions can be installed separately without breaking core functionality
3. **Better Error Messages**: If an extension isn't installed, you get a helpful error message
4. **Cleaner API**: Users can access extensions via `my_framework.ext` instead of `my_framework_ext`
5. **Flexible Installation**: Users can install just the core, or use the meta package for everything

## Package Installation Patterns

This demo shows three common Python packaging patterns:

### 1. Minimal Installation (Core Only)
```bash
pip install -e ./core
```
For users who only need the core functionality and want to keep dependencies minimal.

### 2. À la Carte Installation
```bash
pip install -e ./core
pip install -e ./extension
```
For users who want to install specific extensions they need. Thanks to lazy loading, even if an extension is installed, it won't be imported until used.

### 3. Complete Installation (Meta Package)
```bash
pip install -e ./meta
```
For users who want everything installed at once. The meta package (`my-framework-complete`) declares both `my-framework` and `my-framework-ext` as dependencies, so one command installs all packages. This pattern is used by:
- **Jupyter** (`jupyter` installs `jupyter-core`, `notebook`, `qtconsole`, etc.)
- **Ansible** (`ansible` installs `ansible-core` and multiple collections)
- **Django-CMS** (meta package installs core and common plugins)

## Testing Without the Extension

Try uninstalling the extension package:

```bash
pip uninstall -y my-framework-ext
```

Then modify `demo.py` to comment out the extension usage:

```python
import sys

print("1. Importing core framework...")
import my_framework

print("   [Check] Is extension loaded in sys.modules?", "my_framework_ext" in sys.modules)
print("   Core framework imported successfully without extension!")
```

This demonstrates that the core framework works independently.

## Real-World Deployment

In a production environment where packages are published to PyPI, the installation would be much simpler:

### For End Users (Production)
```bash
# Install everything at once
pip install my-framework-complete

# Or install selectively
pip install my-framework              # Core only
pip install my-framework my-framework-ext  # Core + specific extensions
```

### For This Demo (Local Development)
Since the packages aren't published to PyPI, you need to install them from local directories in the correct order (dependencies first):
```bash
pip install -e ./core
pip install -e ./extension
pip install -e ./meta  # Now the dependencies are satisfied
```

The meta package's `pyproject.toml` declares `my-framework` and `my-framework-ext` as dependencies, so when published to PyPI, installing `my-framework-complete` would automatically install both dependencies from PyPI.

## Real-World Use Cases

This pattern is used by several popular Python packages:

- **NumPy**: `numpy.testing` is lazily loaded
- **SciPy**: Various submodules use lazy loading for faster imports
- **Dask**: Extensions are loaded on-demand
- **TensorFlow**: Large submodules are lazily imported

## Learn More

- [PEP 562 - Module `__getattr__` and `__dir__`](https://www.python.org/dev/peps/pep-0562/)
- [Python Import System Documentation](https://docs.python.org/3/reference/import.html)

## License

MIT License - See LICENSE file for details.
