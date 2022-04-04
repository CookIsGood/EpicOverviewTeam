import sys

import os

INTERP = os.path.expanduser("/var/www/u1492425/data/www/epicoverviewteam.space/epicteam/bin/python")
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from start import application