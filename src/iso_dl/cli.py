# iso-dl # CLI #

import atexit
import os
from urllib.request import urlretrieve
from subprocess import Popen, DEVNULL
from time import sleep

import aria2p

from . import DISTROS
from ._distros.core import Distro

ARIA2C_INSTALLED = os.system("which aria2c >/dev/null 2>&1") == 0


def main():
    try:
        _main()
    except KeyboardInterrupt:
        raise SystemExit(1)


def _main():

    from sys import argv

    argv = argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print(
            "Usage: iso-dl (distro | command) [options...]\n\n"
            "Download:\n"
            "  Usage: iso-dl distro\n"
            "  Options:\n"
            "    --arch {arch}      architecture (amd64, armhf, aarch64)\n"
            "    --no-torrent       don't use torrent to download the ISO\n"
            "    --info             don't download the ISO, just print the info\n"
            "\n"
            "List distros:\n"
            "  iso-dl ls [query]"
            #
        )

    elif distro := DISTROS.get(argv[0].lower()):
        if "--info" in argv:
            info(distro)
            return
        dl(
            distro,
            no_torrent="--no-torrent" in argv,
            arch=argv[argv.index("--arch") + 1] if "--arch" in argv else "amd64",
        )

    elif argv[0] in ("ls", "list"):
        ls(argv[1].strip().lower() if len(argv) > 1 else None)

    else:
        ...
        print(f"Invalid distro: {argv[0]}")


def info(distro: Distro):
    print(f"{distro.name} ({distro.version})")
    for arch in distro.architectures:
        print(f"\n{arch.upper()}:")
        for k, v in distro[arch].items():
            if v:
                print(f"  {k.capitalize() + ':' :<12} {v}")


def dl(distro: Distro, no_torrent: bool = False, arch: str | None = None):
    if not arch:
        arch = distro.architectures[0]

    print(f"{distro.name} ({distro.version})\n")

    output_file = None

    # Torrent
    if ARIA2C_INSTALLED:
        aria2 = init_aria2()

        if not no_torrent and distro[arch]["torrent"]:
            torrent = urlretrieve(str(distro[arch]["torrent"]))
            gid = aria2.add_torrent(torrent[0]).gid

        else:
            gid = aria2.add_uris([str(distro[arch]["url"])]).gid

        print(end="\x1b[s", flush=True)

        while True:
            dl = aria2.get_download(gid)

            if not output_file:
                try:
                    output_file = dl.name
                except IndexError:  # needed because of some weird error with aria2p
                    pass

            print(f"\x1b[u\x1b[J  {dl.progress_string(1)}   {dl.download_speed_string()}   {dl.eta_string()}")

            if not dl.is_active or dl.is_complete or (dl.download_speed == 0 and dl.progress == 100):
                break

            sleep(0.5)

        if output_file:
            print(f"\x1b[u\x1b[JSaved to: ./{output_file}")

    # Direct download


def ls(query: str | None):
    for name, distro in DISTROS.items():
        if not query or query in name:
            print(distro.name)


def init_aria2() -> aria2p.API:
    aria2_proccess = Popen(
        # ["aria2c", "--enable-rpc", "--rpc-listen-port=6801", "--rpc-secret=iso-dl"], stdout=DEVNULL, stderr=DEVNULL
        ["aria2c", "--enable-rpc"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )
    atexit.register(lambda: aria2_proccess.send_signal(2))

    fails = 0
    while True:
        try:
            aria2 = aria2p.API(aria2p.Client(host="http://localhost/"))
            aria2.get_downloads()  # check if connection works
            return aria2
        except Exception as e:
            if fails > 50:
                raise e
        sleep(0.2)
        fails += 1
