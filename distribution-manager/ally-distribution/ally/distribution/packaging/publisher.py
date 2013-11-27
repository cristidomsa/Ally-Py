'''
Created on Oct 10, 2013
 
@package: pypi publish
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Simple implementation for publishing components/plugins on pypi.
'''

import logging
from ally.distribution.util import PYTHON_CLI, SETUP_FILENAME, BUILD_EGG, runCmd

# --------------------------------------------------------------------

OFFICIAL_REP = '-r pypi'
REGISTER = 'register'
SOURCE = 'sdist'
BUILD_WIN = 'bdist_wininst'
UPLOAD = 'upload'

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Publisher:
    
    def __init__(self, packageName, packagePath):
        '''
        do nothing
        '''
        assert isinstance(packagePath, str), 'Invalid package path provided %s' % packagePath
        assert isinstance(packageName, str), 'Invalid package name provided %s' % packageName
        self.packageName = packageName
        self.packagePath = packagePath
        
    def publish(self):
        '''
        Register and update a pypi component
        '''
        assert logging.info('*** PUBLISH package *** {0}'.format(self.packageName)) or True
        
        cmd = ' '.join([PYTHON_CLI, SETUP_FILENAME, REGISTER, OFFICIAL_REP, \
                        SOURCE, BUILD_EGG, UPLOAD, OFFICIAL_REP])
        runCmd(self.packagePath, cmd)