from gestura.utils.key_normalizer import KeyUtils, Key, KeyCode
import pytest


def test_str_key():

    assert KeyUtils.parse_key('\x0c', 'str') == "l"
    assert KeyUtils.parse_key('\x01', 'str') == "a"
    assert KeyUtils.parse_key('\x0b', 'str') == "k"
    assert KeyUtils.parse_key('0x01', 'str') == "a"
    assert KeyUtils.parse_key('alt_gr', 'str') == "alt"
    assert KeyUtils.parse_key('ctrl_l', 'str') == "ctrl"

    assert KeyUtils.parse_key(key="ctrl", output_type="object") == Key.ctrl
    assert KeyUtils.parse_key(key="shift", output_type="object") == Key.shift
    assert KeyUtils.parse_key(key="alt", output_type="object") == Key.alt
    assert KeyUtils.parse_key(key="alt_gr", output_type="object") == Key.alt
    assert KeyUtils.parse_key(key="space", output_type="object") == Key.space
    assert KeyUtils.parse_key(key="home", output_type="object") == Key.home
    assert KeyUtils.parse_key(key="esc", output_type="object") == Key.esc

    assert str(KeyUtils.parse_key(key=" ", output_type="object")) == "''" # TODO: most fix.
    assert KeyUtils.parse_key(key="a", output_type="object") == KeyCode.from_char("a")
    assert KeyUtils.parse_key(key="B", output_type="object") == KeyCode.from_char("b") # NOTE: return lower


def test_type_key():

    assert type(KeyUtils.parse_key(key="ctrl", output_type="object")) == Key
    assert type(KeyUtils.parse_key(key=" ", output_type="object")) == KeyCode
