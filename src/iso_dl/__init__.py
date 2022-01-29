from ._distros import DISTROS
from pprint import pprint


pprint([*DISTROS])

pprint(DISTROS["manjaro-community-budgie-minimal"]["amd64"])
