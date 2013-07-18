"""
Load every settings file and override afterwards.

Created on Jul 17, 2013

@author: jnaous, CarolinaFernandez
"""

import sys, traceback

from django import *
from database import *
from admins import *
from email import *
from expedient import *
from logdata import *
from gcf import *
from messaging import *
from openflow import *
from site import *
from xmlrpc import *
from openflowtests import *
from tests import *
from ldapdata import *
from plugin import *
# Import the list of required variables
from required import REQUIRED_SETTINGS

# Try getting importing the secret key from a secret_key module
try:
    from secret_key import SECRET_KEY
except ImportError:
    print(
        "Error importing secret_key module. Using default insecure key."
        "Please run the 'create_secret_key' manage.py command to create "
        "a new secret key. Do this only after setting up your local settings."
        " If you are not yet running the production server, you can ignore "
        "this error."
    )

# Now import the local settings
try:
    # do the import here to check that the path exists before doing anything
    from local import *
    
    # Delete all the default required settings
    _modname = globals()['__name__']
    _this_mod = sys.modules[_modname]
    for item in REQUIRED_SETTINGS:
        for var in item[1]:
            delattr(_this_mod, var)

    # now import again to re-insert the deleted settings
    from local import *

    # check that all the required settings are set
    for item in REQUIRED_SETTINGS:
        for var in item[1]:
            if not hasattr(_this_mod, var):
                raise Exception(
                    "Missing required setting %s. See the "
                    "documentation for this setting at "
                    "%s"
                    % (var, item[0])
                )

except ImportError as e:
    if "No module named local" in "%s" % e:
        print(
            "ERROR: No local module defined. Please run the "
            " 'bootstrap_local_settings' command if you have not yet "
            "created a local module and add the parent "
            "directory to your PYTHONPATH. Proceeding with missing "
            "required settings."
        )
    else:
        raise

# Logging
from common import loggingconf
import logging

if DEBUG:
    loggingconf.set_up(logging.DEBUG, LOGGING_LEVELS)
else:
    loggingconf.set_up(logging.INFO, LOGGING_LEVELS)


#GENI CONTROL FRAMEWORK SETTINGS (NOT NEEDED AT THIS MOMENT)
GCF_BASE_NAME = "expedient//your_affiliation"
GCF_URN_PREFIX = "expedient:your_afiliation"

#OFREG URL
OFREG_URL = " https://register.fp7-ofelia.eu"
OFREG_RESET_PATH = '/password_reset/forgotten'


OPENFLOW_GAPI_RSC_URN_PREFIX = "urn:publicid:IDN+expedient:your_affiliation:openflow"
OPENFLOW_GAPI_AM_URN = OPENFLOW_GAPI_RSC_URN_PREFIX+"+am"

#Openflow Test (NOT NEEDED, BUT KEPT HERE JUST IN CASE)
MININET_VMS = [
    ("84.88.41.12", 22),
]

#Monitoring
MONITORING_INTERVAL = 38
