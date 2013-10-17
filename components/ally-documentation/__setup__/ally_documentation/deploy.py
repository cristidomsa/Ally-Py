'''
Created on Oct 9, 2013

@package: ally documentation
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in application deploy.
'''

from inspect import getdoc
import logging

from ally.container import ioc, deploy, context
from ally.container.context import activate
from application import parser, options

from ..ally.deploy import FLAG_START, prepareActions, preparePreferences
from ..ally_plugin.deploy import plugins
from .service import path_documentation, paths_templates, createDocumentation


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

FLAG_DOCUMENT = 'document'
# Flag indicating the documentation action.

# --------------------------------------------------------------------

@ioc.after(prepareActions)
def prepareDocumentationActions():
    
    dest = options.registerConfiguration(path_documentation)
    
    options.registerFlag(FLAG_DOCUMENT, FLAG_START)
    options.registerFlagLink(dest, FLAG_DOCUMENT)
    
    parser.add_argument('-doc', metavar='folder', nargs='?', dest=dest, help=getdoc(path_documentation))
    

@ioc.after(preparePreferences)
def prepareDocumentationPreferences():
    
    parser.add_argument('--templates', metavar='folder', nargs='+', dest=options.registerConfiguration(paths_templates),
                        help=getdoc(paths_templates))
    
# --------------------------------------------------------------------

@deploy.start
def document():
    if not options.isFlag(FLAG_DOCUMENT): return
    with activate(plugins(), 'document'):
        context.processStart()
        createDocumentation()
