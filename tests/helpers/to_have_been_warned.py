from neopy import console
from unittest.mocl import MagicMock

console.error = MagicMock()
console.warn = MagicMock()


def has_warned(msg, spy=console.error):
    if isinstance(msg, list):
        return any([has_warned(m, spy) for m in msg])
    spy.assert_any_call(msg)
