# iso-dl # distros #

__all__ = ("DISTROS",)

__import__(f"{__name__}.distros")  # load the module containing the distro definitions

from .core import DISTROS
