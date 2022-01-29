from typing import Callable


VALID_ARCHITECTURES = frozenset(["amd64", "i586", "i686", "armhf", "aarch64"])

commasep = lambda x: ", ".join(x)


class Distributions(dict):
    def add(self, f):
        self[f.__name__.lower().replace("_", "-")] = Distro(f)


class Distro:
    __slots__ = ("name", "_version", "_data", "_f")
    distros: dict = {}

    def __init__(self, f: Callable):
        self._f = f
        self._data = None
        self.name = f.__name__.replace("_", "-")

    @property
    def architectures(self) -> list[str]:
        self._assure_urls()
        return [i for i in self._data.keys() if i != "version"]

    @property
    def version(self) -> str:
        self._assure_urls()
        return self._version

    def _assure_urls(self) -> None:
        if not self._data is None:
            return
        # data structure: {
        #   version
        #   architectur (e.g. x86_64): {
        #       ?url
        #       ?torrent (url to torrent file)
        #       ?magnet
        #       ?hash (e.g. sha256)
        #   }
        # }
        data: dict = self._f()

        # verify data structure
        if not "version" in data:  # verison is required
            raise ValueError("missing version")
        self._version = data.pop("version")

        # replace x86_64 with amd64
        if "x86_64" in data:
            data["amd64"] = data.pop("x86_64")

        # verify the architectures
        if invalid := set(data.keys()) - VALID_ARCHITECTURES:
            raise ValueError(f"invalid architecture: {commasep(invalid)}")

        # for each architecture:
        for arch_name, arch_data in data.items():
            # verify data structure
            if invalid := set(arch_data.keys()) - {"url", "torrent", "md5", "sha256", "sha1"}:
                raise ValueError(f"invalid keys for architecture {arch_name}: {commasep(invalid)}")

            # if a key is set to None, remove it
            for key in [*arch_data.keys()]:
                if arch_data[key] is None:
                    arch_data.pop(key)

        self._data = data

    def __getitem__(self, key: str) -> dict[str, str]:
        self._assure_urls()
        if key == "x86_64":
            key = "amd64"
        if not key in self._data.keys():
            raise KeyError(
                f"No ISO available for architecture {key}. Valid architectures: {commasep(self.architectures)}"
            )
        return self._data[key]

    def __repr__(self) -> str:
        return f"Distro('{self.name}')"
