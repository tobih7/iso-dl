# iso-dl # distros #

import re
from requests import get
from .core import add
from .utils import *


# archlinux #
@add()  # as of January 2022
def archlinux():
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


# Manjaro #
# as of January 2022
def manjaro(edition, minimal, lts, community):  # as of January 2022
    url = f"https://gitlab.manjaro.org/webpage/manjaro-homepage/-/raw/master/site/content/downloads/{'community' if community else 'official'}/{edition}.md"
    data = dict_keys_to_lowercase(parse_key_value_pairs(get(url).text))
    return {
        "version": data["version"],
        "amd64": {
            "url": data[f"download{minimal}{lts or '_x64'}"],
            "torrent": data[f"download{minimal}_x64_torrent{lts}"],
            "sha1": data[f"download{minimal}_x64_checksum{lts}"],
        },
    }


for edition in ("xfce", "kde", "gnome"):
    for minimal, lts in (("", ""), ("_minimal", ""), ("_minimal", "_lts")):
        add(f"manjaro-{edition.upper()}{minimal}{lts.upper()}", edition, minimal, lts, False)(manjaro)

for edition in ("budgie", "cinnamon", "i3", "mate"):  # sway is too complicated
    for minimal in ("", "_minimal"):
        add(f"manjaro-community-{edition}{minimal}", edition, minimal, "", True)(manjaro)


# Debian #
@add()  # as of January 2022
def Debian():
    baseurl = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd"
    data = get(f"{baseurl}/SHA256SUMS")
    sha256, version = re.findall(r"^([a-f0-9]+)\s*debian-(.+)-amd64-netinst.iso$", data.text, re.M | re.I)[0]
    return {
        "version": version,
        "amd64": {
            "url": f"{baseurl}/debian-{version}-amd64-netinst.iso",
            "sha256": sha256,
        },
    }


# KDE Neon #
for edition in ("user", "testing", "unstable", "developer"):

    @add(f"KDE-Neon-{edition}".removesuffix("-user"), edition)  # as of February 2020
    def _(edition):
        baseurl = f"https://files.kde.org/neon/images/{edition}/current"
        data = get(f"{baseurl}/neon-{edition}-current.sha256sum")
        sha256, version = re.findall(rf"^([a-f0-9]+)\s*neon-{edition}-(.+).iso$", data.text, re.M | re.I)[0]
        return {
            "version": version,
            "amd64": {
                "url": f"{baseurl}/neon-{edition}-{version}.iso",
                "torrent": f"{baseurl}/neon-{edition}-{version}.iso.torrent",
                "sha256": sha256,
            },
        }


# Archcraft #
@add()  # as of March 2022
def Archcraft():
    data = get_links_from_url("https://archcraft.io/download")
    by_end = lambda end: [i for i in data if i.endswith(end)][0]
    return {
        "version": re.findall(r"download/v(.+)/archcraft", iso := by_end(".iso"), re.I)[0],
        "amd64": {
            "url": iso,
            "torrent": by_end(".torrent"),
            "sha256": get(by_end(".sha256sum")).text.split()[0],
        },
    }
