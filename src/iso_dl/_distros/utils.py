# iso-dl # distros # utils #

import re
import requests
from bs4 import BeautifulSoup

__all__ = ("parse_key_value_pairs", "dict_keys_to_lowercase", "get_links_from_url")


def parse_key_value_pairs(key_value_pairs: str) -> dict[str, str]:
    """
    Parser for this format:
    key1 = value1
    key2 = value2
    """
    return dict(re.findall(r"^(.*\S)\s*=\s*[\"'`]{0,1}(.*[^\"'`\n])[\"'`]{0,1}$", key_value_pairs, re.M))


def dict_keys_to_lowercase(dict: dict) -> dict:
    return {key.lower(): value for key, value in dict.items()}


def get_links_from_url(url: str) -> list[str]:
    """
    Get all links from a given url.
    """

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    return [link.get("href") for link in soup.find_all("a")]
