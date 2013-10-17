'''
Created on Oct 2, 2013

@package: ally distribution
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup for general resources.
'''

from .request_api import external_host, external_port
from .service import packager, path_components
from ally.container import support, deploy
from distribution import parser, options
import logging

# --------------------------------------------------------------------

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(message)s')
logging.getLogger('ally.distribution').setLevel(logging.INFO)

FLAG_PACKAGE = 'package'
# Flag indicating the packaging action.

# --------------------------------------------------------------------

@deploy.prepare
def prepare():
    
    options.location = None
    options.host = None
    options.port = None
    
    options.registerFlagTrue(FLAG_PACKAGE)
    
    parser.add_argument('--location', metavar='folder', dest='location', help='The location where '
                        'the distribution results should be placed, if none provided it will default to '
                        'a location based on the performed action.')
    parser.add_argument('--host', dest='host', help='The host from where to fetch API data, this is used '
                        'only for services that require API data from a deployed application, if not specified '
                        'it will default to "localhost".')
    parser.add_argument('--port', dest='port', type=int, help='The port to use with the host, if not specified '
                        'it will default to "8080".')

@deploy.start
def deploy():
    if options.host: support.force(external_host, options.host)
    if options.port: support.force(external_port, options.port)
    if options.isFlag(FLAG_PACKAGE):
        location = getattr(options, 'location', None)
        if location: support.force(path_components, location)
        packager().generateSetupFiles()
