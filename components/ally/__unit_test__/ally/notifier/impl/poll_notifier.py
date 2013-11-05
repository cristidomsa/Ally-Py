'''
Created on Sep 11, 2013

@author: mihaigociu

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Tests the notifier.

'''
# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

import logging
import unittest

from ally.container.ioc import initialize
from ally.design.processor.assembly import Assembly
from ally.design.processor.execution import Processing, FILL_ALL
from ally.notifier.impl.processor.register import RegisterListeners
from ally.notifier.impl.processor.scanner_file_system import FileSystemScanner


# --------------------------------------------------------------------
logging.basicConfig()
logging.getLogger('ally.design.processor').setLevel(logging.INFO)
logging.getLogger('ally.notifier').setLevel(logging.DEBUG)

# --------------------------------------------------------------------

class TestConfigurationParsing(unittest.TestCase):

    def testConfigurationParser(self):
        ''' '''
        assemblyScanning = Assembly('Files scanner')
        registerListeners = RegisterListeners()
        registerListeners.patterns = ['file:///home/mihaigociu/Work/notifier_test/test1.txt',
                                      'file:///home/mihaigociu/Work/*/test1.txt']
        
        assemblyScanning.add(initialize(registerListeners), initialize(FileSystemScanner()))
        # assemblyScanning.add(initialize(RegisterListeners()))
        
        proc = assemblyScanning.create()
        assert isinstance(proc, Processing)
        
        proc.execute(FILL_ALL)

if __name__ == '__main__': unittest.main()
        
