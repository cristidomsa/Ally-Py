'''
Created on Feb 1, 2013

@package: service gateway
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the server configuration.
'''

from ..ally_http.server import assemblyServer, updateAssemblyServer
from .processor import assemblyGateway, server_provide_gateway, GATEWAY_EXTERNAL
from ally.container import ioc
from ally.design.processor.handler import Handler, RoutingHandler

# --------------------------------------------------------------------

@ioc.entity
def gatewayRouter() -> Handler: return RoutingHandler(assemblyGateway())

# --------------------------------------------------------------------

@ioc.before(updateAssemblyServer)
def updateAssemblyServerForGatewayExternal():
    if server_provide_gateway() == GATEWAY_EXTERNAL: assemblyServer().add(gatewayRouter())
