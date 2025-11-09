"""Unit tests for data_scrubber utilities."""

import pytest
from datetime import datetime
from analytics_project.data_prep.data_scrubber import (
    standardize_id,
    clean_string,
    standardize_numeric,
    standardize_date,
    remove_outliers,
    handle_missing_values,
    remove_duplicates
)

def test_standardize_id():
    """Test ID standardization with various inputs."""
    assert standardize_id('123', width=4) == '0123'
    assert standardize_id(None, width=4) == '0000'
    assert standardize_id('ABC123', width=4) == '0123'
    assert standardize_id(456, width=4) == '0456'
    assert standardize_id('', width=4) == '0000'
    assert standardize_id('123', width=4, prefix='P') == 'P0123'

def test_clean_string():
    """Test string cleaning and standardization."""
    assert clean_string('hello  world') == 'Hello World'
    assert clean_string(None) == 'Unknown'
    assert clean_string('') == 'Unknown'
    assert clean_string('LA city') == 'LA City'
    assert clean_string('NYC area') == 'NYC Area'
    assert clean_string('  extra  spaces  ') == 'Extra Spaces'

def test_standardize_numeric():
    """Test numeric value standardization."""
    assert standardize_numeric('123.456') == '123.46'
    assert standardize_numeric(None) == '0.00'
    assert standardize_numeric('1,234.56') == '1234.56'
    assert standardize_numeric('50%') == '0.50'
    assert standardize_numeric('abc') == '0.00'
    assert standardize_numeric('100', min_value=0, max_value=50) == '50.00'
    assert standardize_numeric('-10', min_value=0) == '0.00'

def test_standardize_date():
    """Test date string standardization."""
    assert standardize_date('2025-11-08') == '2025-11-08'
    assert standardize_date('11/08/2025') == '2025-11-08'
    assert standardize_date('08-11-2025') == '2025-11-08'
    assert standardize_date('20251108') == '2025-11-08'
    today = datetime.now().strftime('%Y-%m-%d')
    assert standardize_date(None) == today
    assert standardize_date('invalid') == today

def test_remove_outliers():
    """Test outlier removal using different methods."""
    data = [
        {'value': '10'}, {'value': '20'}, {'value': '30'},
        {'value': '1000'}, {'value': '15'}, {'value': '25'}
    ]
    
    # Test IQR method
    cleaned = remove_outliers(data, 'value', method='iqr')
    assert len(cleaned) == 5  # 1000 should be removed
    assert all(row in cleaned for row in data if row['value'] != '1000')
    
    # Test z-score method
    cleaned = remove_outliers(data, 'value', method='zscore', threshold=2)
    assert len(cleaned) == 5  # 1000 should be removed
    
    # Test empty data
    assert remove_outliers([], 'value') == []
    
    # Test invalid method
    with pytest.raises(ValueError):
        remove_outliers(data, 'value', method='invalid')

def test_handle_missing_values():
    """Test missing value handling with defaults."""
    data = [
        {'id': '1', 'name': 'Test', 'value': '10'},
        {'id': '2', 'name': '', 'value': '?'},
        {'id': '3', 'name': None, 'value': ','},
        {'id': '', 'name': 'Skip', 'value': '20'}
    ]
    
    defaults = {
        'name': 'Unknown',
        'value': '0'
    }
    
    required = ['id']
    
    cleaned = handle_missing_values(data, defaults, required)
    assert len(cleaned) == 3  # Last row should be skipped (missing id)
    assert cleaned[1]['name'] == 'Unknown'
    assert cleaned[1]['value'] == '0'

def test_remove_duplicates():
    """Test duplicate removal using different key configurations."""
    data = [
        {'id': '1', 'name': 'Test1'},
        {'id': '1', 'name': 'Test2'},
        {'id': '2', 'name': 'Test3'},
        {'id': '2', 'name': 'Test3'}
    ]
    
    # Test single key
    cleaned = remove_duplicates(data, 'id')
    assert len(cleaned) == 2
    
    # Test multiple keys
    cleaned = remove_duplicates(data, ['id', 'name'])
    assert len(cleaned) == 3
    
    # Test with missing key
    cleaned = remove_duplicates(data, 'missing')
    assert len(cleaned) == 1  # All rows have same key (None)