#!/usr/bin/python

# WARNING: this file is not under version control, and is unique for
# each environment. Make sure doesn't have any interesting code.

import sys

# Which settings file to load for this environment
SETTINGS = 'dev'

sys.path.insert(0, "/Users/ben/Sites/laststatement/laststatement/htdocs")

activate_this = "/Users/ben/envs/last/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

from last.app import app
