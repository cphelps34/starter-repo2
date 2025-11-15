"""Common utilities for data cleaning and standardization across preparation scripts."""

import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


def standardize_id(value: Any, width: int = 6, prefix: str = "") -> str:
    """Standardize an ID to a fixed-width string with optional prefix.

    Args:
        value: The ID value to standardize
        width: Number of digits to pad to (default: 6)
        prefix: Optional prefix to add (default: '')

    Returns:
        Standardized ID string padded with zeros
    """
    try:
        # Handle None, empty strings, etc
        if not value and value != 0:
            return "0" * width

        # Remove any non-digit characters and convert to int
        clean_value = "".join(c for c in str(value) if c.isdigit())
        if not clean_value:
            return "0" * width

        return f"{prefix}{str(int(clean_value)).zfill(width)}"
    except (ValueError, TypeError):
        return "0" * width


def clean_string(value: Any, default: str = "Unknown") -> str:
    """Clean and standardize a string value.

    Args:
        value: The string value to clean
        default: Default value if input is None/empty (default: 'Unknown')

    Returns:
        Cleaned string with proper spacing and capitalization
    """
    if not value and value != 0:
        return default

    # Convert to string, strip whitespace, normalize spaces
    cleaned = " ".join(str(value).strip().split())

    # Title case but preserve common abbreviations
    abbreviations = {"LA", "NYC", "US", "UK"}
    words = cleaned.split()
    titled_words = []

    for word in words:
        upper_word = word.upper()
        if upper_word in abbreviations:
            titled_words.append(upper_word)
        else:
            titled_words.append(word.title())

    return " ".join(titled_words)


def standardize_numeric(
    value: Any,
    default: float = 0.0,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    decimals: int = 2,
) -> str:
    """Standardize a numeric value with validation and formatting.

    Args:
        value: The numeric value to standardize
        default: Default value if parsing fails (default: 0.0)
        min_value: Optional minimum allowed value
        max_value: Optional maximum allowed value
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted numeric string with specified decimals
    """
    try:
        if not value and value != 0:
            return f"{default:.{decimals}f}"

        # Remove commas and spaces, handle percentages
        clean_value = str(value).replace(",", "").replace(" ", "")
        if clean_value.endswith("%"):
            clean_value = str(float(clean_value[:-1]) / 100)

        # Convert to float and validate range
        number = float(clean_value)
        if min_value is not None:
            number = max(number, min_value)
        if max_value is not None:
            number = min(number, max_value)

        return f"{number:.{decimals}f}"
    except (ValueError, TypeError):
        return f"{default:.{decimals}f}"


def standardize_date(
    value: Any, default: Optional[str] = None, output_format: str = "%Y-%m-%d"
) -> str:
    """Standardize a date string with flexible input parsing.

    Args:
        value: The date string to standardize
        default: Default date string if parsing fails (default: today)
        output_format: Desired output format (default: YYYY-MM-DD)

    Returns:
        Formatted date string
    """
    if default is None:
        default = datetime.now().strftime(output_format)

    if not value:
        return default

    # List of common date formats to try
    date_formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%b %d %Y",
        "%B %d %Y",
        "%Y%m%d",
        "%m/%d/%y",
        "%d/%m/%y",
        "%y-%m-%d",
    ]

    # Try parsing with each format
    for fmt in date_formats:
        try:
            date = datetime.strptime(str(value).strip(), fmt)
            return date.strftime(output_format)
        except ValueError:
            continue

    return default


def remove_outliers(
    data: List[Dict[str, Any]], field: str, method: str = "iqr", threshold: float = 1.5
) -> List[Dict[str, Any]]:
    """Remove outliers from a numeric field using various methods.

    Args:
        data: List of dictionaries containing the data
        field: Name of the numeric field to check for outliers
        method: Method to use ('iqr' or 'zscore', default: 'iqr')
        threshold: Threshold for outlier detection (default: 1.5 for IQR)

    Returns:
        List of dictionaries with outliers removed
    """
    if not data:
        return []

    # Extract numeric values, handling missing/invalid values
    values = []
    for row in data:
        try:
            value = float(standardize_numeric(row.get(field, 0)))
            values.append(value)
        except (ValueError, TypeError):
            continue

    if not values:
        return data

    if method.lower() == "iqr":
        # Calculate quartiles and IQR
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1

        # Define bounds
        lower = q1 - (threshold * iqr)
        upper = q3 + (threshold * iqr)

        # Filter outliers
        return [
            row
            for row in data
            if lower <= float(standardize_numeric(row.get(field, 0))) <= upper
        ]

    elif method.lower() == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        # Filter using z-score
        return [
            row
            for row in data
            if abs((float(standardize_numeric(row.get(field, 0))) - mean) / stdev)
            <= threshold
        ]

    else:
        raise ValueError(f"Unsupported outlier removal method: {method}")


def handle_missing_values(
    data: List[Dict[str, Any]],
    defaults: Dict[str, Any],
    required_fields: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Handle missing values in data using specified defaults.

    Args:
        data: List of dictionaries containing the data
        defaults: Dictionary mapping field names to default values
        required_fields: Optional list of fields that must not be missing

    Returns:
        List of dictionaries with missing values handled
    """
    if required_fields is None:
        required_fields = []

    cleaned_data = []

    for row in data:
        # Skip rows missing required fields
        if any(row.get(field) in (None, "", "?", ",") for field in required_fields):
            continue

        # Create new row with defaults applied
        cleaned_row = {}
        for field, value in row.items():
            if value in (None, "", "?", ","):
                cleaned_row[field] = defaults.get(field, value)
            else:
                cleaned_row[field] = value

        cleaned_data.append(cleaned_row)

    return cleaned_data


def remove_duplicates(
    data: List[Dict[str, Any]], key_fields: Union[str, List[str]]
) -> List[Dict[str, Any]]:
    """Remove duplicate records based on key field(s).

    Args:
        data: List of dictionaries containing the data
        key_fields: Field name(s) to use as unique key(s)

    Returns:
        List of dictionaries with duplicates removed
    """
    if isinstance(key_fields, str):
        key_fields = [key_fields]

    seen = set()
    unique_data = []

    for row in data:
        # Create tuple of values for key fields
        key = tuple(str(row.get(field, "")) for field in key_fields)

        if key not in seen:
            seen.add(key)
            unique_data.append(row)

    return unique_data
