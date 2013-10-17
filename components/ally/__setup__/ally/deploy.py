'''
Created on Oct 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in application deploy.
'''

from logging import FileHandler
import logging
import os
import sys
import unittest

from ally.container import event, ioc, context, aop, support, deploy
from ally.container.impl.config import load, save
from ally.design.priority import Priority, PRIORITY_NORMAL
from application import parser, options

from .logging import format, debug_for, info_for, warning_for, log_file


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

PRIORITY_PREFERENCE = Priority('Preference', after=PRIORITY_NORMAL)
# The priority for setting the application preference arguments.

PRIORITY_LOGGING = Priority('Logging', before=PRIORITY_NORMAL)
# The priority for setting up logging.
PRIORITY_CONFIGURATION = Priority('Configure', before=PRIORITY_LOGGING)
# The priority for setting the application configurations.

FLAG_CONFIGURE = 'configure'
# Flag indicating the application configurations.
FLAG_START = 'start'
# Flag indicating the application start.
FLAG_DUMP = 'dump'
# Flag indicating the application should dump configurations.
FLAG_TEST = 'test'
# Flag indicating the application should perform unit testing.
FLAG_REPAIR = 'repair'
# Flag indicating the application should perform repair events in the distribution.

# --------------------------------------------------------------------

@deploy.prepare
def prepareActions():
    
    options.registerFlagTrue(FLAG_CONFIGURE)
    options.registerFlagTrue(FLAG_START)
    options.registerFlag(FLAG_DUMP, FLAG_START)
    options.registerFlag(FLAG_TEST, FLAG_START)
    options.registerFlag(FLAG_REPAIR, FLAG_START)
    
    parser.add_argument('-dump', dest=FLAG_DUMP, action='store_true',
                        help='Provide this option in order to write all the configuration files and exit')
    parser.add_argument('-test', dest=FLAG_TEST, action='store_true',
                        help='Provide this option in order to run the unit tests in the application distribution')
    parser.add_argument('-repair', dest=FLAG_REPAIR, action='store_true',
                        help='Provide this option in order to run the application distribution repair, this will'
                        ' trigger all default data and resources to be populated')

@deploy.prepare(PRIORITY_PREFERENCE)
def preparePreferences():
    
    options.configuration = 'application.properties'
    
    parser.add_argument('--ccfg', metavar='file', dest='configuration',
                        help='The path of the components properties file to be used in deploying the application, '
                        'by default is used the "application.properties" in the current folder.')

# --------------------------------------------------------------------

@deploy.start(PRIORITY_CONFIGURATION)
def configureApplication():
    if not options.isFlag(FLAG_CONFIGURE): return
    context.configurationsLoad(configurations())

@deploy.start(PRIORITY_LOGGING)
def loggingApplication():
    logging.basicConfig(format=format())
    for name in warning_for(): logging.getLogger(name).setLevel(logging.WARN)
    for name in info_for(): logging.getLogger(name).setLevel(logging.INFO)
    for name in debug_for(): logging.getLogger(name).setLevel(logging.DEBUG)
    
    if log_file(): logging.getLogger().addHandler(FileHandler(log_file()))
        
@deploy.start
def start():
    if not options.isFlag(FLAG_START): return
    if not os.path.isfile(options.configuration):
        log.warn('The configuration file "%s" doesn\'t exist, create one by running the the application '
                 'with "-dump" option', options.configuration)
    context.processStart()

@deploy.start
def dump():
    if not options.isFlag(FLAG_DUMP): return
    if not __debug__:
        log.error('Cannot dump configuration file if python is run with "-O" or "-OO" option')
        sys.exit(1)
    # Forcing the processing of all configurations
    saveConfigurations(context.configurationsExtract())

@deploy.start
def test():
    if not options.isFlag(FLAG_TEST): return
    classes = aop.classesIn('__unit_test__.**.*').asList()
    classes = [clazz for clazz in classes if issubclass(clazz, unittest.TestCase)]
    if not classes:
        log.info('-' * 71)
        log.info('No unit test available')
        sys.exit(1)
    testLoader, runner, tests = unittest.TestLoader(), unittest.TextTestRunner(stream=sys.stdout), unittest.TestSuite()
    for clazz in classes: tests.addTest(testLoader.loadTestsFromTestCase(clazz))
    runner.run(tests)

@deploy.start
def repair():
    if not options.isFlag(FLAG_REPAIR): return
    support.performEventsFor(event.REPAIR)
            
# --------------------------------------------------------------------

@ioc.entity
def configurations():
    if os.path.isfile(options.configuration):
        with open(options.configuration, 'r') as f: return load(f)
    return {}

# --------------------------------------------------------------------
    
def saveConfigurations(config):
    '''Saves the application configurations.
    *Attention this function is only available in an opened deploy assembly.*
    
    :param config: The configurations to save
    :type config: dict{str: object}.
    '''
    if os.path.isfile(options.configuration):
        os.rename(options.configuration, '%s.%s' % (options.configuration, 'bak'))
    with open(options.configuration, 'w') as f: save(config, f)
    log.info('Updated the \'%s\' configuration file', options.configuration)
