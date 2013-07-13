# coding: utf-8

# Use settings files to store passwords, secret keys, and other configuration
# that will change depending on environment. Enter name of settings file in
# index.py. For instance, you may have dev.py, prod.py, and stage.py under
# settings. In production environment, index.py should set SETTINGS = 'prod'
#
# Add the settings files to .gitignore so your secrets don't get out!

SQLURI = "postgresql://laststatement:SecretPassword@localhost/laststatement"
SECRET = "ThisShouldBeALongRandomStringWithNumbersAndSymbols"
DEBUG = False
