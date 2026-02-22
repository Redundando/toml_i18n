try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from pathlib import Path
from collections import defaultdict
from contextvars import ContextVar
from typing import Optional

class Default(dict):
    """
    A dictionary subclass that returns an empty string for missing keys.
    """
    def __missing__(self, key):
        return ''


_instance_var: ContextVar['TomlI18n'] = ContextVar('toml_i18n_instance', default=None)

class TomlI18n:
    def __init__(self, locale: str, fallback_locale: str = "en", directory: str = "i18n"):
        """
        Initialize the I18n class for managing internationalized strings.

        This class uses contextvars for context-local storage, enabling safe concurrent
        use in async applications. It loads localized strings from TOML files, supports
        a fallback locale, and provides easy access to translations.

        Args:
            locale (str): The primary locale to use for translations (e.g., 'en', 'fr').
            fallback_locale (str): The fallback locale to use if a key is missing in the primary locale.
                                  Defaults to 'en'.
            directory (str): The directory containing the localization TOML files. Defaults to 'i18n'.
        """
        self.locale = locale
        self.fallback_locale = fallback_locale
        self.directory = Path(directory)
        self.strings = self._load_all_strings(locale)
        self.fallback_strings = self._load_all_strings(fallback_locale)
        _instance_var.set(self)

    @classmethod
    def is_initialized(cls) -> bool:
        return _instance_var.get() is not None

    @classmethod
    def initialize(cls, locale: str="en", fallback_locale: str = "en", directory: str = "i18n"):
        """
        Initialize a context-local instance of the I18n class.

        This method sets up a context-local I18n instance for managing translations.
        In async applications, each task gets its own isolated instance. In synchronous
        code, it behaves like a global singleton. Always creates a fresh instance.

        Args:
            locale (str): The primary locale to use for translations (e.g., 'en', 'fr').
            fallback_locale (str): The fallback locale to use if a key is missing in the
                                   primary locale. Defaults to 'en'.
            directory (str): The directory containing the localization TOML files.
                             Defaults to 'i18n'.
        """
        cls(locale, fallback_locale, directory)

    @classmethod
    def get_instance(cls):
        """Get the context-local instance."""
        instance = _instance_var.get()
        if instance is None:
            raise Exception("TomlI18n not initialized. Call TomlI18n.initialize() first.")
        return instance

    @classmethod
    def get_locale(cls) -> str:
        """Get the current locale."""
        return cls.get_instance().locale

    @classmethod
    def get_available_locales(cls) -> list[str]:
        """Get list of available locales based on TOML files in directory."""
        instance = cls.get_instance()
        locales = set()
        for file in instance.directory.glob("*.*.toml"):
            parts = file.stem.split(".")
            if len(parts) >= 2:
                locales.add(parts[-1])
        return sorted(locales)

    @classmethod
    def has_key(cls, key: str) -> bool:
        """Check if a translation key exists in current or fallback locale."""
        instance = cls.get_instance()
        return (instance._get_string(key, instance.strings) is not None or 
                instance._get_string(key, instance.fallback_strings) is not None)

    def _load_all_strings(self, locale: str) -> dict:
        """Load and merge all TOML files for a given locale."""
        merged_strings = defaultdict(dict)
        for file in self.directory.glob(f"*.{locale}.toml"):
            with open(file, "rb") as f:  # tomllib requires binary mode
                data = tomllib.load(f)
                for key, value in data.items():
                    if key in merged_strings:
                        merged_strings[key].update(value)  # Merge nested dictionaries
                    else:
                        merged_strings[key] = value
        return dict(merged_strings)  # Convert default dict to a regular dict

    @classmethod
    def get(cls, key: str, count: Optional[int] = None, **kwargs) -> str:
        """
        Retrieve a localized string for the given key, with support for parameter formatting and fallback locale.
        
        Args:
            key (str): The translation key (e.g., 'general.greeting')
            count (int, optional): For pluralization. Looks for key_zero, key_one, key_other variants
            **kwargs: Named parameters for string formatting
        """
        instance = cls.get_instance()
        
        # Handle pluralization
        if count is not None:
            if count == 0:
                plural_key = f"{key}_zero"
            elif count == 1:
                plural_key = f"{key}_one"
            else:
                plural_key = f"{key}_other"
            
            value = instance._get_string(plural_key, instance.strings)
            if value is None:
                value = instance._get_string(plural_key, instance.fallback_strings)
            
            # Fall back to base key if plural form not found
            if value is None:
                value = instance._get_string(key, instance.strings)
            if value is None:
                value = instance._get_string(key, instance.fallback_strings)
            
            kwargs['count'] = count
        else:
            value = instance._get_string(key, instance.strings)
            if value is None:
                value = instance._get_string(key, instance.fallback_strings)
        
        if value is None:
            return f"Missing translation for '{key}'"
        return value.format_map(Default(**kwargs))

    def _get_string(self, key: str, strings: dict) -> Optional[str]:
        """Helper method to retrieve a string by key."""
        keys = key.split(".")
        value = strings
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return None  # Key not found

    def set_locale(self, locale: str, fallback_locale: Optional[str] = None):
        """Change the locale and reload the strings."""
        self.locale = locale
        self.strings = self._load_all_strings(locale)
        if fallback_locale:
            self.fallback_locale = fallback_locale
        self.fallback_strings = self._load_all_strings(self.fallback_locale)

    def format_number(self, number, decimals: Optional[int] = 0) -> str:
        """
        Format a number according to the current locale, with optional decimal precision.
        Note: Uses basic formatting without locale.setlocale() to avoid thread-safety issues.
        """
        if not isinstance(number, (int, float)):
            raise ValueError(f"Input must be an int or float, got: {type(number)}")
        
        if decimals is None:
            return f"{number:,.12f}".rstrip("0").rstrip(".")
        return f"{number:,.{decimals}f}"

def i18n(key: str, count: Optional[int] = None, **kwargs):
    """
        Retrieve a localized string for the given key, ensuring the I18n class is initialized.

        This utility function simplifies access to localized strings. If the I18n class
        has not been initialized, it initializes it with default settings.

        Args:
            key (str): The dot-separated key to retrieve the localized string (e.g., 'general.greeting').
            count (int, optional): For pluralization. Looks for key_zero, key_one, key_other variants.
            **kwargs: Named parameters to format the localized string (e.g., `name="John"`).

        Returns:
            str: The localized string with the parameters formatted.

        Example:
            # Access a localized string without worrying about initialization
            print(i18n("general.greeting", name="Alice"))
            print(i18n("items.count", count=5))  # Uses items.count_other

        Raises:
            Exception: If the I18n class cannot be initialized or the key cannot be retrieved.
        """

    if not TomlI18n.is_initialized():
        TomlI18n.initialize()
    return TomlI18n.get(key, count=count, **kwargs)

def i18n_number(number, decimals: Optional[int] = None):
    """
    Format a number according to the current locale using TomlI18n.

    If TomlI18n has not been initialized, it will initialize with default settings.

    Args:
        number (int | float | str): The number to format. Strings will be converted to numbers if valid.
        decimals (int, optional): Number of decimal places to display. If None, defaults to the locale's rules.

    Returns:
        str: The formatted number as a string.
    """
    if not TomlI18n.is_initialized():
        TomlI18n.initialize()

    return TomlI18n.get_instance().format_number(number, decimals=decimals)
