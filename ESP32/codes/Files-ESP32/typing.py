# typing.py - Minimal stub for MicroPython

# Import basic types from collections.abc if available
try:
    from collections.abc import Iterable, Iterator, Sequence, Mapping, Callable
except ImportError:
    # Fallback definitions if collections.abc is not available
    Iterable = Iterator = Sequence = Mapping = Callable = object

# Define minimal aliases for type hints
Any = object
Optional = lambda x: x
List = list
Dict = dict

# For most MLX90640 functions, this stub should suffice.
# If you encounter further issues, we can add more definitions as needed.
