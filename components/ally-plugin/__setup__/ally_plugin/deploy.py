'''
Created on Oct 8, 2013

@package: ally plugin
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in application deploy.
'''

import logging
import os
import re

from ally.container import ioc, context, support, aop, event, app, deploy
from ally.container.context import activate
from ally.container.error import SetupError
from ally.container.impl.config import save, load
from ally.design.priority import Priority, PRIORITY_FIRST
from ally.support.util_sys import isPackage
from application import parser, options
import application
from package_extender import PACKAGE_EXTENDER

from ..ally.deploy import PRIORITY_PREFERENCE, dump, FLAG_DUMP, \
    preparePreferences
from .distribution import application_mode, PRIORITY_PERSIST_MARKERS, \
    triggerEvents


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

PRIORITY_PREPARE_PLUGIN = Priority('Prepare plugin', after=PRIORITY_PREFERENCE)
# The priority for setting the application preference arguments.

PRIORITY_DEPLOY = Priority('Deploy plugin', after=PRIORITY_FIRST)
# The deploy priority.
PRIORITY_TRIGGER_EVENTS = Priority('Deploy plugin events', before=PRIORITY_PERSIST_MARKERS)
# The deploy event priority.

# --------------------------------------------------------------------

@ioc.after(preparePreferences)
def preparePluginPreferences():
    
    options.mode = None
    
    parser.add_argument('--mode', metavar='MODE', nargs=1, dest='mode',
                        help='Provide this option in order to override the \'application_mode\' configuration in the '
                        'application properties')

@deploy.prepare(PRIORITY_PREPARE_PLUGIN)
def preparePreferences():
    
    application.parser = parser.add_argument_group('ally-py application plugins options.')
    with activate(plugins(), 'deploy'): support.performEventsFor(deploy.APP_PREPARE)
    application.parser = parser

# --------------------------------------------------------------------
     
@ioc.after(dump)
def dumpPlugins():
    if not options.isFlag(FLAG_DUMP): return
    saveConfigurations(context.configurationsExtract(plugins()))

@ioc.start(priority=PRIORITY_DEPLOY)
def start():
    if not os.path.isfile(path_configuration()):
        log.warn('The configuration file \'%s\' does not exist, create one by running the the application '
                 'with "-dump" option', path_configuration())
    with activate(plugins(), 'start'):
        context.configurationsLoad(configurations())
        triggerEvents(app.SETUP)
        context.processStart()
    
@ioc.start(priority=PRIORITY_TRIGGER_EVENTS)
def startEvents():
    with activate(plugins(), 'events'): triggerEvents(app.DEPLOY, app.POPULATE)

@event.on(event.REPAIR)
def repairEvents():
    with activate(plugins(), 'repair'): triggerEvents(app.REPAIR)

@ioc.before(application_mode)
def updateApplicationMode():
    if options.mode: support.force(application_mode, options.mode)

# --------------------------------------------------------------------

@ioc.config
def path_configuration():
    '''
    The name of the configuration file for the plugins.
    '''
    return 'plugins.properties'

# --------------------------------------------------------------------

@ioc.entity
def plugins():
    PACKAGE_EXTENDER.addFreezedPackage('__plugin__.')
    pluginModules = aop.modulesIn('__plugin__.**')
    for module in pluginModules.load().asList():
        if not isPackage(module) and re.match('__plugin__\\.[^\\.]+$', module.__name__):
            raise SetupError('The plugin setup module \'%s\' is not allowed directly in the __plugin__ package it needs '
                             'to be in a sub package' % module.__name__)

    return context.open(pluginModules, included=True)

# --------------------------------------------------------------------

@ioc.entity
def configurations():
    if os.path.isfile(path_configuration()):
        with open(path_configuration(), 'r') as f: return load(f)
    return {}

# --------------------------------------------------------------------

def saveConfigurations(config):
    '''Saves the plugins configurations.
    *Attention this function is only available in an opened deploy assembly.*
    
    :param config: The configurations to save
    :type config: dict{str: object}.
    '''
    if os.path.isfile(path_configuration()):
        os.rename(path_configuration(), '%s.%s' % (path_configuration(), 'bak'))
    with open(path_configuration(), 'w') as f: save(config, f)
    log.info('Updated the \'%s\' configuration file', path_configuration())
