# 99/100

"""
tests:
    test_key_utils.py
"""

from typing import Optional, Union, Literal, overload
from functools import lru_cache
import re

from pynput.keyboard import Key, KeyCode


class KeyUtils:
    MODIFIER_PATTERN = re.compile(r".*(ctrl|control|shift|alt|cmd|win|meta).*", re.IGNORECASE)

    SIMPLE_MODIFIERS = {
        "ctrl": Key.ctrl,
        "control": Key.ctrl,
        "shift": Key.shift,
        "alt": Key.alt,
        "altgr": Key.alt,
        "alt_gr": Key.alt,
        "cmd": Key.cmd,
        "win": Key.cmd,
        "meta": Key.cmd,
    }

    HEX_PATTERN = re.compile(r"^0x([0-9a-f]{2})$", re.IGNORECASE)

    @staticmethod
    def is_modifier(key: Optional[Union[Key, KeyCode, str]]) -> bool:
        if key is None:
            return False

        if isinstance(key, Key):
            name = str(key)[4:].lower() if str(key).startswith("Key.") else str(key).lower()

        elif isinstance(key, KeyCode):
            name = key.char.lower() if key.char else ""

        else:
            # here key is guaranteed to be str
            name = key.lower()

        return bool(KeyUtils.MODIFIER_PATTERN.match(name))

    @staticmethod
    def normalize_modifier_name(name: str) -> str:
        name = name.strip()
        if "ctrl" in name or "control" in name:
            return "ctrl"
        if "shift" in name:
            return "shift"
        if "alt" in name:
            return "alt"
        if "cmd" in name or "win" in name or "meta" in name:
            return "cmd"
        return name.lower()

    @staticmethod
    @lru_cache(maxsize=512)
    def control_char_to_key(char: str) -> Optional[str]:
        if len(char) != 1:
            return None
        code = ord(char)
        if 1 <= code <= 26:
            return chr(code + 96)
        return None

    @staticmethod
    @lru_cache(maxsize=2048)
    def _normalize_key_str(name: str) -> str:
        # If the input is a hex string like '0x0c', map it if in control range
        m = KeyUtils.HEX_PATTERN.match(name.lower())
        if m:
            code = int(m.group(1), 16)
            if 1 <= code <= 26:
                return chr(code + 96)
            else:
                return name.lower()

        # If input is single char (including control chars), try to map to letter
        if len(name) == 1:
            mapped = KeyUtils.control_char_to_key(name)
            if mapped:
                return mapped

        # Else normalize modifiers
        return KeyUtils.normalize_modifier_name(name.strip())

    @overload
    @staticmethod
    def normalize_key(key: Optional[Union[Key, KeyCode, str]], output_type: Literal["object"]) -> Union[Key, KeyCode]: ...
    @overload
    @staticmethod
    def normalize_key(key: Optional[Union[Key, KeyCode, str]], output_type: Literal["str"]) -> str: ...
    @overload
    @staticmethod
    def normalize_key(key: Optional[Union[Key, KeyCode, str]], output_type: Literal["type"]) -> str: ...

    @staticmethod
    def normalize_key(
        key: Optional[Union[Key, KeyCode, str]],
        output_type: Literal["object", "str", "type"] = "object"
    ) -> Union[Key, KeyCode, str]:

        if key is None:
            if output_type == "str":
                return ""
            if output_type == "type":
                return "KeyCode"
            return KeyCode.from_char("")

        elif isinstance(key, str):
            name = key

            # Remove 'key.' prefix and surrounding quotes but do NOT strip (important for control chars)
            if name.startswith("key."):
                name = name[4:]
            if name.startswith("'") and name.endswith("'") and len(name) > 1:
                name = name[1:-1]

            norm_name = KeyUtils._normalize_key_str(name)

            if output_type == "str":
                return norm_name
            if output_type == "type":
                if len(norm_name) == 1:
                    return "KeyCode"
                if KeyUtils.is_modifier(norm_name):
                    return "Key"
                return "Key" if hasattr(Key, norm_name) else "KeyCode"
            if output_type == "object":
                if norm_name in KeyUtils.SIMPLE_MODIFIERS:
                    return KeyUtils.SIMPLE_MODIFIERS[norm_name]
                if hasattr(Key, norm_name):
                    return getattr(Key, norm_name)
                return KeyCode.from_char(norm_name if len(norm_name) == 1 else "")

        elif isinstance(key, Key):
            base = str(key)[4:] if str(key).startswith("Key.") else str(key)
            norm = KeyUtils.normalize_modifier_name(base)
            if output_type == "str":
                return norm
            if output_type == "type":
                return "Key"
            if output_type == "object":
                if norm in KeyUtils.SIMPLE_MODIFIERS:
                    return KeyUtils.SIMPLE_MODIFIERS[norm]
                return key

        # elif isinstance(key, KeyCode):
        # here most KeyCode
        if output_type == "object":
            return key if key.char is not None else KeyCode.from_char("")
        if output_type == "str":
            return key.char if key.char else ""
        if output_type == "type":
            return "KeyCode"

    @staticmethod
    @overload
    def parse_key(key: Optional[Union[Key, KeyCode, str]], output_type: Literal["object"]) -> Union[Key, KeyCode]: ...
    @staticmethod
    @overload
    def parse_key(key: Optional[Union[Key, KeyCode, str]], output_type: Literal["str"]) -> str: ...
    @staticmethod
    @overload
    def parse_key(key: Optional[Union[Key, KeyCode, str]], output_type: Literal["type"]) -> str: ...

    @staticmethod
    def parse_key(
        key: Optional[Union[Key, KeyCode, str]],
        output_type: Literal["object", "str", "type"] = "object"
    ) -> Union[Key, KeyCode, str]:
        return KeyUtils.normalize_key(key, output_type=output_type)
