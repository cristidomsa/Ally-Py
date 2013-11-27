'''
Created on Oct 31, 2013
 
@package: ally.distribution
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Provides configuration mechanisms used in distribution manager.
'''

from configparser import SafeConfigParser
import os
import sys

# --------------------------------------------------------------------

class Config:
    '''
    Class used for generating configuration files.
    '''
    
    def __init__(self, packageName, packagePath):
        '''
        do nothing
        '''
        assert isinstance(packagePath, str), 'Invalid package path provided %s' % packagePath
        assert isinstance(packageName, str), 'Invalid package name provided %s' % packageName
        self.packageName = packageName
        self.packagePath = packagePath
        
    def writeCfgFiles(self, configOptions):
        '''
        fills the configuration object with data from configOptions and writes the configuration file   
        '''
        os.chdir(self.packagePath)
        for filename, content in configOptions.items():
            if os.path.isfile(filename): return 1
            with open(filename, 'w') as f:
                parser = self._generateParser(content)
                parser.write(f)
    
# --------------------------------------------------------------------
    def _generateParser(self, configOptions):
        '''
        Generates content to be written from configOptions dictionary
        '''
        parser = SafeConfigParser()
        for section, content in configOptions.items():
            parser.add_section(section)
            if isinstance(content, dict):
                for option, value in content.items():
                    value = value.format(inputPath=self.packageName) if 'inputPath' in value else value
                    parser.set(section, option, value)
        return parser