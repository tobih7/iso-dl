import re

__all__ = ("parse_key_value_pairs", "dict_keys_to_lowercase")


def parse_key_value_pairs(key_value_pairs: str) -> dict[str, str]:
    return dict(re.findall(r"^(.*\S)\s*=\s*[\"'`]{0,1}(.*[^\"'`\n])[\"'`]{0,1}$", key_value_pairs, re.M))


def dict_keys_to_lowercase(dict: dict) -> dict:
    return {key.lower(): value for key, value in dict.items()}
