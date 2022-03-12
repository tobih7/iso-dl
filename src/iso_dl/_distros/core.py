# iso-dl # distros #

from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Any, Callable, Literal, Optional, Tuple, get_args

__all__ = (
    "Distro",
    "URL",
    "Torrent",
    "Magnet",
    "Hash",
    "Architecture",
    "VALID_ARCHITECTURES",
    "HashType",
    "VALID_HASHTYPES",
)


# @dataclass(frozen=True)
# class ISO:
#     url: Optional[str] = None
#     torrent: Optional[str] = None
#     magnet: Optional[str] = None
#     sha256: Optional[str] = None
#     sha1: Optional[str] = None
#     md5: Optional[str] = None


Architecture = Literal["amd64", "armhf", "aarch64"]  # x86_64 is always replaced with amd64
VALID_ARCHITECTURES: Tuple[Architecture, ...] = get_args(Architecture)

HashType = Literal["sha256", "sha1", "md5"]
VALID_HASHTYPES: Tuple[HashType, ...] = get_args(HashType)


class Distro:
    __slots__ = ("__func", "__initialized", "__func_args", "__func_kwargs", "__name", "__version", "__archs")

    def __init__(
        self,
        func: Callable[[], Optional[dict[str, Any]]],
        /,
        name: Optional[str] = None,
        func_kwargs: Optional[dict[str, Any]] = None,
        func_args: Optional[tuple[Any]] = None,
    ):
        """
        :param func: function that returns a dict with the following keys:
            - version: version of the distro (str)
            - arch?: dict with the following keys
                - url?: URL to the ISO
                - torrent?: URL to the torrent file
                - magnet?: magnet link
                - sha256?: SHA256 hash
                - sha1?: SHA1 hash
                - md5?: MD5 hash
            - to indicate an error None can be returned
        :param name: name of the distro (str)
            - if not given, the name is extracted from the function name
        :param func_args: arguments to pass to the function
        :param func_kwargs: keyword arguments to pass to the function
            - useful when e.g. the function is defined inside a loop and the some
            variables are not available anymore or have changed at the time of the call
        """
        assert callable(func)
        assert isinstance(name, str) or name is None
        assert isinstance(func_args, tuple) or func_args is None
        assert isinstance(func_kwargs, dict) or func_kwargs is None

        self.__func = func
        self.__func_args = func_args or tuple()
        self.__func_kwargs = func_kwargs or {}
        self.__name = name or parse_distro_name(func.__name__)
        self.__initialized = False

    def __initialize(self) -> None:
        if self.__initialized:
            return

        try:
            data = self.__func(*self.__func_args, **self.__func_kwargs)
        except Exception as exc:
            raise Exceptions.DistroInitializationFailure(f"failed to initialize distro") from exc

        # verify data
        assert isinstance(data, dict), "must return dict"

        if data is None:
            raise Exceptions.DistroInitializationFailure("failed to initialize distro")

        # version
        if not "version" in data:
            raise Exceptions.DistroInitializationFailure("missing version")
        self.__version = data.pop("version")

        # architectures
        if "x86_64" in data:
            data["amd64"] = data.pop("x86_64")
        archs: dict[str, dict[str, str]] = {i: data.pop(i) for i in list(data.keys()) if i in VALID_ARCHITECTURES}
        if data:  # data should be empty now
            raise Exceptions.DistroInitializationFailure(f"Invalid architectures: {', '.join(data.keys())}")

        self.__archs: dict[str, dict[str, Any]] = {}
        for name, content in archs.items():
            if invalid := {*content.keys()} - {*VALID_HASHTYPES, "url", "torrent", "magnet"}:
                raise Exceptions.DistroInitializationFailure(f"Invalid keys: {', '.join(invalid)}")

            self.__archs[name] = {
                "url": URL(url) if (url := content.pop("url", None)) else None,
                "torrent": Torrent(torrent) if (torrent := content.get("torrent")) else None,
                "magnet": Magnet(magnet) if (magnet := content.get("magnet")) else None,
            }
            for ht in VALID_HASHTYPES:
                if value := content.get(ht):
                    self.__archs[name]["hash"] = Hash(ht, value)
                    break  # one hash is enough

        self.__initialized = True

    @property
    def name(self) -> str:
        return self.__name

    @property
    def version(self) -> str:
        self.__initialize()
        return self.__version

    @property
    def architectures(self) -> list[str]:
        self.__initialize()
        return list(self.__archs.keys())

    def __getitem__(self, key: str) -> Any:
        if key == "x86_64":
            key = "amd64"
        if not key in VALID_ARCHITECTURES:
            raise KeyError(f"Invalid architecture: {key}")
        if key in self.architectures:
            self.__initialize()
            return self.__archs[key]
        else:
            raise KeyError(key)

    def __repr__(self) -> str:
        return f"<Distro {self.name!r}>"


class BaseURI(ABC):
    __slots__ = ("__uri",)

    def __init__(self, uri: str):
        self.validate(uri)
        self.__uri = uri

    @staticmethod
    @abstractmethod
    def validate(uri: str) -> bool:
        pass

    def __str__(self) -> str:
        return self.__uri

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.__uri!r}>"


class URL(BaseURI):
    @staticmethod
    def validate(uri: str) -> bool:
        # TODO: validate URI
        return True


class Torrent(URL):  # just an URL to a torrent file
    pass


class Magnet(BaseURI):
    @staticmethod
    def validate(uri: str) -> bool:
        # TODO: validate URI
        return True


class Hash:
    __slots__ = ("__type", "__value")

    def __init__(self, type: HashType, value: str):
        self.__type: HashType = type
        self.__value: str = value

    def type(self) -> HashType:
        return self.__type

    def value(self) -> str:
        return self.__value

    def __str__(self) -> str:
        return self.__value

    def __repr__(self) -> str:
        return f"<Hash {self.__type} {self.__value!r}>"


class Exceptions:
    class DistroInitializationFailure(Exception):
        pass


def parse_distro_name(name: str) -> str:
    name = re.sub(r"\s+|_+", "-", name)
    assert re.match(r"^[a-zA-Z0-9-]+$", name) is not None, "name must only consist of a-z, A-Z, 0-9 and -"
    return name


DISTROS: dict[str, Distro] = {}


def add(name: Optional[str] = None, *args, **kwargs) -> Callable[[Callable[..., Any]], None]:
    assert isinstance(name, str) or name is None, "name must be str or None"
    name = name and parse_distro_name(name)

    def decorator(func: Callable[..., Optional[dict[str, Any]]]) -> None:
        # if no name was provided, get it by the function name
        DISTROS[(name or distro.name).lower()] = (distro := Distro(func, name=name, func_args=args, func_kwargs=kwargs))

    return decorator
