'''
Created on Oct 30, 2013
 
@package: ally.distribution
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
The scanner used for extracting the localized text messages and generate PO file.
'''

from ally.distribution.util import PYTHON_CLI, SETUP_FILENAME, runCmd
import logging
from ally.distribution.templates import SETUP_CFG_UI_OPTIONS, BABEL_CFG_OPTIONS
from ally.distribution.packaging.config import Config

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

EXTRACT_CMD = 'extract_messages'
GENERATE_CMD = 'init_catalog'

# --------------------------------------------------------------------

class Scanner:
    '''
    The class that provides the localization messages scanner.
    '''

    def __init__(self, packageName, packagePath):
        '''
        do nothing
        '''
        assert isinstance(packagePath, str), 'Invalid package path provided %s' % packagePath
        assert isinstance(packageName, str), 'Invalid package name provided %s' % packageName
        self.packageName = packageName
        self.packagePath = packagePath
    
    def prepareUIPlugin(self):
        '''
        Prepares the env for ui plugin actions
        '''
        assert log.info('*** {name} *** Configuration *** STARTED'.format(name=self.packageName)) or True
        cfg = Config(self.packageName, self.packagePath)
        configuration = SETUP_CFG_UI_OPTIONS
        configuration.update(BABEL_CFG_OPTIONS)
        cfg.writeCfgFiles(configuration)
        assert log.info('*** {name} *** Configuration *** DONE'.format(name=self.packageName)) or True
    
    def scan(self):
        '''
        babel action to do
        '''
        self.prepareUIPlugin()
        self.extractMessages()
        
    def extractMessages(self):
        '''
        Scan the current package and extract the localized text messages.
        '''
        assert log.info('-' * 50) or True
        assert log.info('*** Scanning UI plugin *** {0} ***'.format(self.packageName)) or True
    
        cmd = ' '.join([PYTHON_CLI, SETUP_FILENAME, EXTRACT_CMD])
        runCmd(self.packagePath, cmd)
        
    def generatePO(self):
        '''
        Generates PO file based on the POT file generated after scanning the package
        '''
        assert log.info('*** Generating PO file *** {0} ***'.format(self.packageName)) or True
    
        cmd = ' '.join([PYTHON_CLI, SETUP_FILENAME, GENERATE_CMD])
        runCmd(self.packagePath, cmd)