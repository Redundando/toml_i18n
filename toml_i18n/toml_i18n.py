import tomllib
from pathlib import Path
from collections import defaultdict
import locale as lc

class TomlI18n:
    _instance = None  # Singleton instance

    def __init__(self, locale: str, fallback_locale: str = "en", directory: str = "toml_i18n"):
        """
        Initialize the I18n class for managing internationalized strings.

        This class implements a singleton pattern to ensure only one instance exists.
        It loads localized strings from TOML files, supports a fallback locale,
        and provides easy access to translations.

        Args:
            locale (str): The primary locale to use for translations (e.g., 'en', 'fr').
            fallback_locale (str): The fallback locale to use if a key is missing in the primary locale.
                                  Defaults to 'en'.
            directory (str): The directory containing the localization TOML files. Defaults to 'toml_i18n'.

        Raises:
            Exception: If an instance of the I18n class already exists (singleton pattern).
        """
        if TomlI18n._instance is not None:
            raise Exception("Localizer is a singleton. Use Localizer.initialize() to set it up.")
        self.locale = locale
        self.fallback_locale = fallback_locale
        self.directory = Path(directory)
        self.strings = self._load_all_strings(locale)
        self.fallback_strings = self._load_all_strings(fallback_locale)
        TomlI18n._instance = self

    @classmethod
    def is_initialized(cls) -> bool:
        return cls._instance is not None

    @classmethod
    def initialize(cls, locale: str="en", fallback_locale: str = "en", directory: str = "i18n"):
        """
        Initialize the singleton instance of the I18n class.

        This method sets up the global I18n instance for managing translations. If the
        instance has already been initialized, it updates the locale and fallback_locale
        while retaining the singleton behavior. Use this method to set up the I18n class
        before accessing translations.

        Args:
            locale (str): The primary locale to use for translations (e.g., 'en', 'fr').
            fallback_locale (str): The fallback locale to use if a key is missing in the
                                   primary locale. Defaults to 'en'.
            directory (str): The directory containing the localization TOML files.
                             Defaults to 'toml_i18n'.

        Raises:
            Exception: If the class is accessed without first calling `initialize`.
        """
        if cls._instance is None:
            cls(locale, fallback_locale, directory)
        else:
            cls._instance.set_locale(locale, fallback_locale)

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            raise Exception("Localizer not initialized. Call Localizer.initialize() first.")
        return cls._instance

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
        return dict(merged_strings)  # Convert defaultdict to a regular dict

    @classmethod
    def get(cls, key: str, **kwargs) -> str:
        """
        Retrieve a localized string for the given key, with support for parameter formatting and fallback locale.
        """
        instance = cls.get_instance()
        value = instance._get_string(key, instance.strings)  # Try primary locale
        if value is None:
            value = instance._get_string(key, instance.fallback_strings)  # Try fallback locale
        if value is None:
            return f"Missing translation for '{key}'"
        return value.format(**kwargs)

    def _get_string(self, key: str, strings: dict) -> str:
        """Helper method to retrieve a string by key."""
        keys = key.split(".")
        value = strings
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return None  # Key not found

    def set_locale(self, locale: str, fallback_locale: str = None):
        """Change the locale and reload the strings."""
        self.locale = locale
        self.strings = self._load_all_strings(locale)
        if fallback_locale:
            self.fallback_locale = fallback_locale
        self.fallback_strings = self._load_all_strings(self.fallback_locale)

    def format_number(self, number:int|float, decimals: int = 0) -> str:
        """
        Format a number according to the current locale, with optional decimal precision.
        """
        try:
            if not isinstance(number, (int, float)):
                raise ValueError(f"Input must be an int, float, or valid numeric string, got: {type(number)}")

            try:
                lc.setlocale(lc.LC_NUMERIC, self.locale)
            except lc.Error:
                lc.setlocale(lc.LC_NUMERIC, self.fallback_locale)  # Fallback to default locale

            format_str = "%f" if decimals is None else f"%.{decimals}f"
            formatted_number = lc.format_string(format_str, number, grouping=True)
            if decimals is None:
                formatted_number = formatted_number.rstrip("0").rstrip(".")

            return formatted_number
        except ValueError as e:
            raise ValueError(f"Could not format number: {e}")

def i18n(key: str, **kwargs):
    """
        Retrieve a localized string for the given key, ensuring the I18n class is initialized.

        This utility function simplifies access to localized strings. If the I18n class
        has not been initialized, it initializes it with default settings.

        Args:
            key (str): The dot-separated key to retrieve the localized string (e.g., 'general.greeting').
            **kwargs: Named parameters to format the localized string (e.g., `name="John"`).

        Returns:
            str: The localized string with the parameters formatted.

        Example:
            # Access a localized string without worrying about initialization
            print(toml_i18n("general.greeting", name="Alice"))

        Raises:
            Exception: If the I18n class cannot be initialized or the key cannot be retrieved.
        """

    if not TomlI18n.is_initialized():
        TomlI18n.initialize(locale="en", fallback_locale="en", directory="toml_i18n")
    return TomlI18n.get(key, **kwargs)

def i18n_number(number, decimals: int = None):
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
        TomlI18n.initialize(locale="en", fallback_locale="en", directory="i18n")

    return TomlI18n.get_instance().format_number(number, decimals=decimals)
