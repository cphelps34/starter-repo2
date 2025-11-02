# API Reference

## Functions

### `hello()`

```python
def hello(name: str) -> str
```

Returns a greeting message for the given name.

**Parameters:**
- `name` (str): The name to greet

**Returns:**
- str: A greeting message

**Example:**
```python
from starter_repo2 import hello
result = hello("Alice")
assert result == "Hello, Alice!"
```