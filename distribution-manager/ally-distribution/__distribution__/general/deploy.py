'''
Created on Oct 2, 2013

@package: ally distribution
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup for general resources.
'''

from .service import packagerPlugins, packagerComponents, path_components, \
    package_location, path_plugins
from ally.container import support, deploy
from distribution import parser, options
from pydoc import getdoc
import logging

# --------------------------------------------------------------------

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(message)s')
logging.getLogger('ally.distribution').setLevel(logging.INFO)

FLAG_PACKAGE = 'package'
# Flag indicating the packaging action.
FLAG_BUILD_EGGS = 'build'
# Flag indicating the build eggs action.
FLAG_BUILD_COMPONENT = 'packageComponent'
FLAG_BUILD_PLUGIN = 'packagePlugins'

# --------------------------------------------------------------------

@deploy.prepare
def prepare():
    
    destComponents = options.registerConfiguration(path_components)
    destPlugins = options.registerConfiguration(path_plugins)
    
    options.location = None
    
    options.registerFlagTrue(FLAG_PACKAGE)
    options.registerFlag(FLAG_BUILD_COMPONENT)
    options.registerFlag(FLAG_BUILD_PLUGIN)
    options.registerFlagLink(destComponents, FLAG_BUILD_COMPONENT)
    options.registerFlagLink(destPlugins, FLAG_BUILD_PLUGIN)
    
    parser.add_argument('--location', metavar='folder', dest='location', help='The location where '
                        'the distribution results should be placed, if none provided it will default to '
                        'a location based on the performed action, if packaging is performed it will default to "packaged-eggs" '
                        'in current folder')
    parser.add_argument('--components', metavar='folder', nargs='?', dest=destComponents, help=getdoc(path_components))
    parser.add_argument('--plugins', metavar='folder', nargs='?', dest=destPlugins, help=getdoc(path_plugins))

@deploy.start
def deploy():
    if options.isFlag(FLAG_PACKAGE):
        if options.location: support.force(package_location, options.location)
        onlyComponents, onlyPlugins = options.isFlag(FLAG_BUILD_COMPONENT), options.isFlag(FLAG_BUILD_PLUGIN)
        if not onlyPlugins and not onlyComponents: 
            onlyComponents = onlyPlugins = True 
        if onlyPlugins:
            packagerPlugins().destFolder = options.location
            packagerPlugins().generateSetupFiles()
        if onlyComponents: 
            packagerComponents().destFolder = options.location
            packagerComponents().generateSetupFiles()
