# iso-dl # distros #

import re
from requests import get
from .core import add
from .utils import *


# archlinux
@add()
def archlinux():  # as of January 2022
    baseurl = "https://archlinux.org"
    data = get(f"{baseurl}/releng/releases/json").json()["releases"][0]
    version = data["version"]
    return {
        "version": version,
        "amd64": {
            "url": f"https://mirror.rackspace.com/archlinux{data['iso_url']}",  # official worldwide mirror
            "torrent": f"{baseurl}{data['torrent_url']}",
            "magnet": data["magnet_uri"],
            "md5": data["md5_sum"],
            "sha256": data["sha256_sum"],
            "sha1": data["sha1_sum"],
        },
    }


# Manjaro
# as of January 2022
for edition in ("xfce", "kde", "gnome"):
    for minimal, lts in (("", ""), ("_minimal", ""), ("_minimal", "_lts")):

        @add(f"manjaro-{edition}{minimal}{lts}", edition=edition, minimal=minimal, lts=lts)
        def _(edition, minimal, lts):
            mdurl = "https://gitlab.manjaro.org/webpage/manjaro-homepage/-/raw/master/site/content/downloads/official"
            data = dict_keys_to_lowercase(parse_key_value_pairs(get(f"{mdurl}/{edition}.md").text))
            return {
                "version": data["version"],
                "amd64": {
                    "url": data[f"download{minimal}{lts or '_x64'}"],
                    "torrent": data[f"download{minimal}_x64_torrent{lts}"],
                    "sha1": data[f"download{minimal}_x64_checksum{lts}"],
                },
            }


for edition in ("budgie", "cinnamon", "i3", "mate"):
    for minimal in ("", "_minimal"):

        @add(f"manjaro-community-{edition}{minimal}", edition=edition, minimal=minimal)
        def _(edition, minimal):
            mdurl = "https://gitlab.manjaro.org/webpage/manjaro-homepage/-/raw/master/site/content/downloads/community"
            data = dict_keys_to_lowercase(parse_key_value_pairs(get(f"{mdurl}/{edition}.md").text))
            return {
                "version": data["version"],
                "amd64": {
                    "url": data[f"download{minimal}_x64"],
                    "torrent": data[f"download{minimal}_x64_torrent"],
                    "sha1": data[f"download{minimal}_x64_checksum"],
                },
            }


# Debian
@add()
def Debian():  # as of January 2022
    baseurl = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/"
    data = get(f"{baseurl}/SHA256SUMS")
    if (match := re.search(r"^([a-f0-9]*)\s*debian-(.*)-amd64-netinst.iso$", data.text, re.M | re.I)) is None:
        return None
    sha256, version = match.groups()
    return {
        "version": version,
        "amd64": {
            "url": f"{baseurl}/debian-{version}-amd64-netinst.iso",
            "sha256": sha256,
        },
    }
