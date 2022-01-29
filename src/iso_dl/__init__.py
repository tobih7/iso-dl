from click import group, argument, echo, option
from .classes import VALID_ARCHITECTURES, Distro, commasep
from .download import download_torrent, download_url
from .distros import distros as DISTROS
from typing import Optional


@group()
def main() -> int:
    pass


@main.command()
@argument("query", default="")
def ls(query: Optional[str]):
    """
    List all supported distros.
    """
    query = query.lower()
    distros = sorted(DISTROS)
    for k in distros:
        if not query or k.startswith(query):
            echo(k)


@main.command()
@argument("distro")
@option("--arch")
@option("--torrent", is_flag=True)
def dl(distro: str, arch: str, torrent: bool):
    """
    Download an ISO.
    """
    if not (distro := DISTROS.get(distro.lower())):
        echo("Error: This distro is not supported.")

    distro: Distro

    if not arch:
        if "amd64" in distro.architectures:
            arch = "amd64"
        else:
            echo("Please specify an architecture.")
            echo(f"Supported architectures: {commasep(distro.architectures)}")

    elif not arch in VALID_ARCHITECTURES:
        echo("Error: Invalid architecture.")
        return 1

    if not arch in distro.architectures:
        echo(f"Error: Unsupported architecture: {arch}")
        return 1

    if torrent and "torrent" in distro[arch]:
        d = lambda: download_torrent(distro[arch]["torrent"])
    elif torrent:
        echo("Error: This distro does not support torrent downloads.")
        return 1
    elif "url" in distro[arch]:
        d = lambda: download_url(distro[arch]["url"])
    else:
        echo("Error: No download available.")
        return 1

    echo(f"{distro.name} \x1b[90m(Version {distro.version})\x1b[0m")
    d()
