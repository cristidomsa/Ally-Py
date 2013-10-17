'''
Created on Oct 9, 2013

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in application deploy.
'''

import codecs
import logging
from os import path, makedirs
from uuid import uuid4

from ally.container import ioc, support, context, deploy
from ally.support.util_io import openURI, ReplaceInStream, pipe
from ally.support.util_sys import pythonPath
from application import options, parser

from ..ally.deploy import FLAG_START, saveConfigurations, prepareActions
from ..ally_http.server import server_port, server_type
from .server import send_spec, send_ident, recv_spec, recv_ident


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

FLAG_CONFIG_MONGREL2 = 'configMongrel2'
# Flag indicating the management of full access IPs.

# --------------------------------------------------------------------

@ioc.after(prepareActions)
def prepareMongrel2Actions():
    
    options.mongrel2Folder = None
    options.registerFlag(FLAG_CONFIG_MONGREL2, FLAG_START)
    options.registerFlagLink('mongrel2Folder', FLAG_CONFIG_MONGREL2)
    
    parser.add_argument('-cfg-mongrel2', metavar='folder', dest='mongrel2Folder', nargs='?',
                        help='Provide this option to create the mongrel2 workspace, by default the mongrel2 '
                        'workspace will be created by default in "workspace" in the application folder, '
                        'just provide a new mongrel2 workspace if thats the case, the path can be relative to '
                        'the application folder or absolute')

# --------------------------------------------------------------------

@deploy.start
def configureMongrel2():
    if not options.isFlag(FLAG_CONFIG_MONGREL2): return
    folders = [path.join('mongrel2', name) for name in ('logs', 'run', 'tmp')]
    folders.append(path.join('shared', 'upload'))

    folder = options.mongrel2Folder or 'workspace'
    
    for name in folders:
        folder = path.join(folder, name)
        if not path.isdir(folder): makedirs(folder)
    
    updateConfig = False
    if server_type() != 'mongrel2':
        updateConfig = True
        support.persist(server_type, 'mongrel2')
    
    sendIdent = send_ident()
    if sendIdent is None:
        updateConfig = True
        sendIdent = str(uuid4())
        support.persist(send_ident, sendIdent)
    
    replace = {}
    replace['${send_spec}'] = send_spec()
    replace['${send_ident}'] = sendIdent
    replace['${recv_spec}'] = recv_spec()
    replace['${recv_ident}'] = recv_ident()
    replace['${server_port}'] = str(server_port())

    if updateConfig: saveConfigurations(context.configurationsExtract())
        
    conf = openURI(path.join(pythonPath(), 'resources', 'ally.conf'))
    conf = codecs.getreader('utf8')(conf)
    conf = ReplaceInStream(conf, replace)
    with open(path.join(folder, 'ally.conf'), 'w') as f: pipe(conf, f)
    with open(path.join(folder, 'README-Mongrel2.txt'), 'wb') as f:
        pipe(openURI(path.join(pythonPath(), 'resources', 'README-Mongrel2.txt')), f)
    
    log.info('Configured \'%s\' mongrel2 workspace' % folder)
