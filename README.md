# toml_i18n

[![PyPI version](https://badge.fury.io/py/toml-i18n.svg)](https://pypi.org/project/toml-i18n/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

`toml_i18n` is a lightweight localization module for Python projects. It provides an easy way to manage and retrieve localized strings using TOML files.

## Installation

```bash
pip install toml-i18n
```


## Usage

### Step 1: Create a Directory for Translations

In your project directory, create a subdirectory for your localization files (e.g., `i18n`).

### Step 2: Add a Translation File
Inside the directory, create a TOML file for your localized strings, such as `general.en.toml`:

```toml
[general]

greeting = "Hello {name}!"
```

and

`general.fr.toml`:

```toml
[general]

greeting = "Bonjour {name}!"
```

### Step 3: Initialize `toml_i18n`

Use the `TomlI18n class to set up the module with your desired locales and directory:


```python
from toml_i18n import TomlI18n

TomlI18n.initialize(locale="fr", fallback_locale="en", directory="i18n")
```

This needs to be done only once when running the project.

### Step 4: Retrieve Localized Strings

```python
from toml_i18n import i18n

print(i18n("general.greeting", name="John Doe"))
```

### Step 5: Format Numbers (Optional)

```python
from toml_i18n import i18n_number

print(i18n_number(1234.56, decimals=2))  # Formats according to current locale
```

## Key Features

- Flexible Localization: Load translations from TOML files.
- Fallback Locale: Automatically fall back to a default locale if a key is missing.
- Dynamic Formatting: Use placeholders in your strings for flexible output.
- Singleton Design: Easy setup and global access to translations.
