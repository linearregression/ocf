import amsoil.core.pluginmanager as pm
from vtdelegate import VTDelegate

def setup():
    # setup config keys
    config = pm.getService("config")
    
    delegate = VTDelegate()
    handler = pm.getService('geniv3handler')
    handler.setDelegate(delegate)
