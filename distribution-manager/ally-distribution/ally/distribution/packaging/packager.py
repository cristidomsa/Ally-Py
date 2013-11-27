'''
Created on Sep 30, 2013
 
@package: ally.distribution
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Simple implementation for distribution manager project.
'''

import logging
import os
import sys
from types import ModuleType
import imp
from ally.distribution.util import getDirs, SETUP_FILENAME, SETUP_CFG_FILENAME,\
    INIT_FILENAME
from ally.distribution.templates import SETUP_TEMPLATE_BEGIN, SETUP_TEMPLATE_END,\
    SETUP_CFG_TEMPLATE
# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
ATTRIBUTE_MAPPING = {'VERSION'         : 'version',
                     'AUTHOR'          : 'author',
                     'AUTHOR_EMAIL'    : 'author_email',
                     'KEYWORDS'        : 'keywords',
                     'INSTALL_REQUIRES': 'install_requires',
                     'DESCRIPTION'     : 'description',
                     'LONG_DESCRIPTION': 'long_description',
                     'TEST_SUITE'      : 'test_suite',
                     'CLASSIFIERS'     : 'classifiers',
                     }
EXTRA_DICT_ATT = '__extra__'

INIT_FOLDER_PLUGIN = '__plugin__'
INIT_FOLDER_CORE = '__setup__'

# --------------------------------------------------------------------

class Packager:
    '''
    @todo: update description
    Distribution class for managing requirements, deploy path
    '''
    destFolder = str
    # destination folder to deploy distribution
    
    def __init__(self, packageName, packagePath):
        '''
        do nothing
        '''
        assert isinstance(packagePath, str), 'Invalid package path provided %s' % packagePath
        assert isinstance(packageName, str), 'Invalid package name provided %s' % packageName
        self.packageName = packageName
        self.packagePath = packagePath
        self.info = {}
        
    def package(self):      
        assert log.info('-' * 50) or True
        assert log.info('*** Package name *** {0} ***'.format(self.packageName)) or True
        module = self._getPackageInfoModule()
        if module: 
            self._constructModuleInfo(module)
            self.info['name'] = self.packageName
            assert log.info('*** Setup info import from module {0} *** OK'.format(module.__name__)) or True
            try:
                self._writeSetupFile()
                self._writeSetupCfgFile()
                assert log.info('*** Setup file succesfully writen *** {0} *** OK'.format(self.packagePath)) or True
            except Exception as e:
                assert log.info('*** Setup file writing failed *** {0} *** NOK'.format(self.packageName)) or True
                assert log.error('Error while writing setup files for {0}: {1}'.format(self.packageName, e)) or True
        assert log.info('-' * 50) or True
    
# --------------------------------------------------------------------    

    def _constructModuleInfo(self, module):
        '''
        returns the dict containing information contained in __init__ file
        '''
        
        assert isinstance(module, ModuleType), 'Invalid module name %s' % module
        for attribute, value in ATTRIBUTE_MAPPING.items():
            if hasattr(module, attribute):
                self.info[value] = getattr(module, attribute)
        if hasattr(module, EXTRA_DICT_ATT):
            self.info.update(getattr(module, EXTRA_DICT_ATT))
        
    
    def _writeSetupFile(self):
        '''
        Writes setup.py file to path
        '''
        filename = os.path.abspath(os.path.join(self.packagePath, SETUP_FILENAME))
        with open(filename, 'w') as f:
            f.write(SETUP_TEMPLATE_BEGIN)
            for attribute in self.info:
                f.write(' '*5 + attribute + '=' + repr(self.info[attribute]) + ',\n')
            f.write(SETUP_TEMPLATE_END)
        
    def _writeSetupCfgFile(self):
        '''
        Writes setup.cfg file to path
        '''
        filename = os.path.abspath(os.path.join(self.packagePath, SETUP_CFG_FILENAME))
        with open(filename, 'w') as f:
            f.write(SETUP_CFG_TEMPLATE.format(self.destFolder))
        
    def _getPackageInfoModule(self):
        '''
        Finds __init__.py file in the component/plugin folder
        '''
        folderType = None
        dirs = getDirs(self.packagePath)
        if INIT_FOLDER_PLUGIN in dirs:
            folderType = INIT_FOLDER_PLUGIN
        if INIT_FOLDER_CORE in dirs:
            folderType = INIT_FOLDER_CORE
        if folderType:
            setupPath = os.path.join(self.packagePath, folderType)
            setupDirs = getDirs(setupPath)
            sys.path.append(os.path.abspath(setupPath))
            setupFilePath = os.path.join(self.packagePath, SETUP_FILENAME)
            if (len(setupDirs) != 1):
                assert log.info('''No setup module to configure or more than one setup module in this package! 
                                   *** SKIPING *** {0} ***
                                   '''.format(self.packageName)) or True
            else:
                setupModule = setupDirs[0]
                infoTimestamp = os.path.getmtime(os.path.join(setupPath, setupModule, INIT_FILENAME))
                try:
                    setupTimestamp = os.path.getmtime(setupFilePath)
                except:
                    assert log.info('No setup.py file available. Writing new.') or True 
                    setupTimestamp = -1 
                    if infoTimestamp < setupTimestamp: 
                        assert log.info('*** SKIPPED (no new info found) ***') or True
                    else:
                        try:
                            module = imp.load_source(setupModule, os.path.join(setupPath, setupModule, INIT_FILENAME))
                            return module
                        except:
                            assert log.warning('*** Loading of setup module failed! ***', exc_info=1)
                            