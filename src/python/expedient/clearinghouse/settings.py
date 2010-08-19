'''Pull all the default settings and then all overrides.

Created on Aug 19, 2010

@author: jnaous
'''
import sys

from expedient.clearinghouse.defaultsettings.django import *
from expedient.clearinghouse.defaultsettings.database import *
from expedient.clearinghouse.defaultsettings.admins import *
from expedient.clearinghouse.defaultsettings.email import *
from expedient.clearinghouse.defaultsettings.expedient import *
from expedient.clearinghouse.defaultsettings.gcf import *
from expedient.clearinghouse.defaultsettings.messaging import *
from expedient.clearinghouse.defaultsettings.openflow import *
from expedient.clearinghouse.defaultsettings.site import *
from expedient.clearinghouse.defaultsettings.xmlrpc import *
# Add new default settings here

# Import the list of required variables
from expedient.clearinghouse.defaultsettings.required import REQUIRED_SETTINGS

# Delete all the default required settings
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]
for item in REQUIRED_SETTINGS:
    for var in item[1]:
        delattr(_this_mod, var)
        
# Now import the local settings
from expedient.clearinghouse.localsettings import *

# check that all the required settings are set
for item in REQUIRED_SETTINGS:
    for var in item[1]:
        if not hasattr(_this_mod, var):
            raise Exception(
                "Missing required setting %s. See the "
                "documentation for this setting at "
                "expedient.clearinghouse.defaultsettings.%s"
                % (var, item[0])
            )

# Logging
from expedient.common import loggingconf
import logging
if DEBUG:
    loggingconf.set_up(logging.DEBUG)
else:
    loggingconf.set_up(logging.INFO)
