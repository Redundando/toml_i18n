# toml_i18n

[![PyPI version](https://badge.fury.io/py/toml-i18n.svg)](https://pypi.org/project/toml-i18n/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

`toml_i18n` is a lightweight localization module for Python projects. It provides an easy way to manage and retrieve localized strings using TOML files, with support for async applications, pluralization, and context-local locales.

## Installation

```bash
pip install toml-i18n
```


## Quick Start

```python
from toml_i18n import TomlI18n, i18n

# Initialize once
TomlI18n.initialize(locale="fr", fallback_locale="en", directory="i18n")

# Use anywhere
print(i18n("general.greeting", name="Alice"))  # "Bonjour Alice!"
```

## Usage

### Basic Setup

**Step 1: Create a Directory for Translations**

In your project directory, create a subdirectory for your localization files (e.g., `i18n`).

**Step 2: Add Translation Files**
Inside the directory, create TOML files for your localized strings:

`general.en.toml`:
```toml
[general]
greeting = "Hello {name}!"
```

`general.fr.toml`:
```toml
[general]
greeting = "Bonjour {name}!"
```

**Step 3: Initialize and Use**

```python
from toml_i18n import TomlI18n, i18n

# Initialize once at app startup
TomlI18n.initialize(locale="fr", fallback_locale="en", directory="i18n")

# Retrieve translations anywhere
print(i18n("general.greeting", name="John"))  # "Bonjour John!"
```

### Pluralization

Handle plural forms using `_zero`, `_one`, and `_other` suffixes:

`items.en.toml`:
```toml
[items]
count_zero = "No items"
count_one = "1 item"
count_other = "{count} items"
```

```python
print(i18n("items.count", count=0))   # "No items"
print(i18n("items.count", count=1))   # "1 item"
print(i18n("items.count", count=5))   # "5 items"
```

### Number Formatting

```python
from toml_i18n import i18n_number

print(i18n_number(1234.56, decimals=2))    # "1,234.56"
print(i18n_number(1000000))                # "1,000,000"
```

### Async/Concurrent Applications

Each async task can have its own locale without interference. The package uses Python's `contextvars` to provide context-local storage, ensuring thread-safe and async-safe locale isolation:

```python
import asyncio
from toml_i18n import TomlI18n, i18n

async def handle_request(locale: str):
    TomlI18n.initialize(locale=locale)
    return i18n("general.greeting", name="User")

# Each task gets isolated locale
async def main():
    results = await asyncio.gather(
        handle_request("en"),  # Returns English
        handle_request("fr"),  # Returns French
        handle_request("de"),  # Returns German
    )
```

### Utility Methods

```python
# Get current locale
current = TomlI18n.get_locale()  # "fr"

# List available locales
locales = TomlI18n.get_available_locales()  # ["de", "en", "fr"]

# Check if translation exists
if TomlI18n.has_key("optional.feature"):
    print(i18n("optional.feature"))

# Change locale dynamically
TomlI18n.get_instance().set_locale("de")
```

## Features

- **Flexible Localization**: Load translations from TOML files
- **Fallback Locale**: Automatically fall back to a default locale if a key is missing
- **Dynamic Formatting**: Use placeholders in your strings for flexible output
- **Pluralization**: Built-in support for plural forms (_zero, _one, _other)
- **Async-Safe**: Context-local storage (via `contextvars`) enables safe concurrent use in async applications
- **Lightweight**: Minimal dependencies, works with Python 3.7+

## Links

- **GitHub**: https://github.com/Redundando/toml_i18n
- **PyPI**: https://pypi.org/project/toml-i18n/
