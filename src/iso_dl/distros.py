import re
from requests import get

from .classes import Distributions

distros = Distributions()
add = distros.add


# archlinux
@add
def archlinux():  # as of January 2022
    baseurl = "https://archlinux.org"
    data = get(f"{baseurl}/releng/releases/json").json()["releases"][0]
    version = data["version"]
    return {
        "version": version,
        "amd64": {
            "url": f"https://mirror.rackspace.com/archlinux{data['iso_url']}",  # official worldwide mirror
            "torrent": f"{baseurl}{data['torrent_url']}",
            "md5": data["md5_sum"],
            "sha256": data["sha256_sum"],
            "sha1": data["sha1_sum"],
        },
    }


# Debian
@add
def Debian():  # as of January 2022
    baseurl = "https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/"
    data = get(f"{baseurl}/SHA256SUMS")
    sha256, version = re.search(r"^([a-f0-9]*)\s*debian-(.*)-amd64-netinst.iso$", data.text, re.M | re.I).groups()
    return {
        "version": version,
        "amd64": {
            "url": f"{baseurl}/debian-{version}-amd64-netinst.iso",
            "sha256": sha256,
        },
    }
