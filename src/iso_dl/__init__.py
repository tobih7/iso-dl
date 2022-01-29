from ._distros import DISTROS
from pprint import pprint


pprint([*DISTROS])

print(DISTROS["manjaro-gnome"]["amd64"])
