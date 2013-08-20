'''General Django settings.

@author: jnaous
'''
# Django settings for Expedient project.
import inspect
import os
import sys
import pkg_resources
from utils import append_to_local_setting
import ldap

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(current_dir + '/../../../vt_manager/src/python')

try:
    from local import SRC_DIR as location
    sys.path.append(location)
except ImportError:
    try:
        location = os.path.abspath(pkg_resources.resource_filename(
            pkg_resources.Requirement.parse("expedient"), ""))
    except pkg_resources.DistributionNotFound:
        location = os.path.abspath(
            pkg_resources.resource_filename("expedient", ".."))
    # TODO: Hack!
    if location.endswith("src/python"):
        location = location[:-7]
    else:
        location = location + "/share/expedient"

SRC_DIR = location
'''Base location of non-python source files.'''

try:
    from local import CONF_DIR as location
except ImportError:
    # TODO: Hack!
    location = "/etc/expedient"

CONF_DIR = location
'''Location of local Expedient configuration files.

Example: /etc/expedient/

'''

try:
    from local import STATIC_DOC_ROOT as static_location
except ImportError:
    static_location = os.path.join(SRC_DIR, "../static")
    static_location = '/opt/ofelia/expedient/static'

STATIC_DOC_ROOT = static_location
'''Location of static content.

Example: /srv/www/expedient/

'''

TIME_ZONE = 'America/Los_Angeles'
'''Local time zone for this installation.

Choices can be found here:
http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
although not all choices may be available on all operating systems.
If running in a Windows environment this must be set to the same as your
system time zone.

'''

LANGUAGE_CODE = 'en-us'
'''Language code for this installation. All choices can be found here:
http://www.i18nguy.com/unicode/language-identifiers.html'''

USE_I18N = False
'''If you set this to False, Django will make some optimizations so as not
to load the internationalization machinery.'''

try:
    from local import *
except ImportError:
    pass

#MEDIA_ROOT = os.path.join(STATIC_DOC_ROOT, "media")
MEDIA_ROOT = STATIC_DOC_ROOT
'''Absolute path to the directory that holds media.
Example: "/home/media/media.lawrence.com/"'''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '../static/default'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

SECRET_KEY = '6=egu-&rx7a+h%yjlt=lny=s+uz0$a_p8je=3q!+-^4w^zxkb8'
'''Make this unique, and don't share it with anybody.

This needs to be overridden.

'''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
]
append_to_local_setting(
    "TEMPLATE_LOADERS", TEMPLATE_LOADERS, globals())

MIDDLEWARE_CLASSES = [
#    'common.middleware.exceptionprinter.ExceptionPrinter',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'common.middleware.basicauth.HTTPBasicAuthMiddleware',
    'common.middleware.sitelockdown.SiteLockDown',
    'common.middleware.threadlocals.ThreadLocals',
    'common.permissions.middleware.PermissionMiddleware',
    'geni_legacy.expedient_geni.middleware.CreateUserGID',
]
append_to_local_setting(
    "MIDDLEWARE_CLASSES", MIDDLEWARE_CLASSES, globals(), at_start=True,
)

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'geni_legacy.expedient_geni.backends.GENIRemoteUserBackend',
]
if ENABLE_LDAP_BACKEND:
    AUTHENTICATION_BACKENDS.insert(1,'django_auth_ldap.backend.LDAPBackend')

append_to_local_setting(
    "AUTHENTICATION_BACKENDS", AUTHENTICATION_BACKENDS, globals(),
)
  
ROOT_URLCONF = 'modules.urls'


TEMPLATE_DIRS = [
    os.path.join(SRC_DIR, 'templates/default/'),
    #os.path.join(SRC_DIR, 'modules/'),
    #os.path.join(SRC_DIR, 'modules/aggregate/templates/default/'),
    #os.path.join(SRC_DIR, 'modules/project/templates/default'),

    #os.path.join(SRC_DIR, 'templates/default/expedient/clearinghouse'),
    #os.path.join(SRC_DIR, 'templates/default/expedient/common'),
    #os.path.join(SRC_DIR, 'templates/common'),
    #os.path.join(SRC_DIR, 'python/vt_plugin/views/templates/default'),
]
append_to_local_setting(
    "TEMPLATE_DIRS", TEMPLATE_DIRS, globals(),
)


INSTALLED_APPS = [
    'modules.firstapp', # Must remain first!
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_extensions',
    'autoslug',
    'registration',
    'django_evolution',
    'common.timer',
    'common.permissions',
    'common.breadcrumbs',
    'common.rpc4django',
    'common.utils',
    'common.extendable',
    'common.xmlrpc_serverproxy',
    'common.messaging',
    'common.defaultsite',
    'modules.commands',
    'modules.aggregate',
    'modules.roles',
    'modules.project',
    'modules.resources',
    'modules.slice',
    'modules.users',
    'modules.permissionmgmt',
#    'openflow.plugin',
    'geni_legacy.expedient_geni',
    'geni_legacy.expedient_geni.planetlab',
    'geni_legacy.expedient_geni.gopenflow',
#    'expedient.ui.html',
    'modules.rspec',
#    'vt_plugin',
#    'vt_plugin.communication',
#    'openflow.dummyom',
#    'sample_resource',
]
append_to_local_setting(
    "INSTALLED_APPS", INSTALLED_APPS, globals(), at_start=True,
)

LOGIN_REDIRECT_URL = '/'

AUTH_PROFILE_MODULE = "users.UserProfile"

ACCOUNT_ACTIVATION_DAYS = 3
'''Number of days account activation links are valid.'''

AGGREGATE_LOGOS_DIR = "aggregate_logos/default/img/aggregates/"
'''Directory relative to MEDIA_ROOT where all aggregate logos are uploaded.'''

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'common.messaging.context_processors.messaging',
    'common.utils.context_processors.contextSettingsInTemplate',
]
append_to_local_setting(
    "TEMPLATE_CONTEXT_PROCESSORS", TEMPLATE_CONTEXT_PROCESSORS, globals())
'''See Django documentation.'''

# Enable debugging?
DEBUG = True
'''Enable/Disable debugging mode. See Django docs on this setting.'''

try:
    from local import *
except ImportError:
    pass

TEMPLATE_DEBUG = DEBUG
'''See Django documentation.'''

DEBUG_PROPAGATE_EXCEPTIONS = DEBUG
'''See Django documentation.'''

SESSION_COOKIE_NAME = "ch_sessionid"
'''Session cookie names to avoid cookie name conflicts.'''

# workaround to allow test:// schemes
import urlparse
urlparse.uses_netloc.append("test")
urlparse.uses_fragment.append("test")

