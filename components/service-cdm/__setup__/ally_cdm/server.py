'''
Created on Feb 1, 2013

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the server configuration.
'''

from ..ally_http.server import assemblyServer, updateAssemblyServer
from .processor import assemblyContent
from ally.container import ioc
from ally.design.processor.handler import Handler
from ally.http.impl.processor.router_by_path import RoutingByPathHandler
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@ioc.config
def server_provide_content():
    ''' Flag indicating that this server should provide content from the local configured repository path'''
    return True

@ioc.config
def root_uri_content():
    '''
    The pattern used for matching the content paths in HTTP URL's
    '''
    return 'content'

# --------------------------------------------------------------------

@ioc.entity
def contentRouter() -> Handler:
    b = RoutingByPathHandler()
    b.assembly = assemblyContent()
    b.rootURI = root_uri_content()
    return b

# We need to make sure that if the CDM is deployed with the gateway that the CDM has priority over the gateway.
updateBefore = [updateAssemblyServer]
try: from ..ally_gateway.server import updateAssemblyServerForGatewayExternal
except ImportError: log.info('No gateway service to register with')
else: updateBefore.append(updateAssemblyServerForGatewayExternal)
@ioc.before(*updateBefore)
def updateAssemblyServerForContent():
    if server_provide_content(): assemblyServer().add(contentRouter())
del updateBefore  # Cleaning up
