
'''
Created on Oct 31, 2013
 
@package: ally.distribution
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Broker used for different actions needed by the distribution manager.
'''
from ally.distribution.util import getDirs, SETUP_FILENAME
import logging
import os
from ally.distribution.templates import SETUP_UI_TEMPLATE
from ally.container.ioc import injected

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class Broker:
        
    actions = dict
    #actions to be performed with information
    path_ui = str
    #The path to the ui source folder
    actionWorker = dict
    #the mapping of workers based on different actions
    destFolder = str
    #destination folder to copy eggs
        
    def __init__(self):
        '''
        Constructor
        '''
        assert isinstance(self.actions, dict), 'Invalid actions dictionary %s' % self.actions
        assert isinstance(self.path_ui, str), 'Invalid ui plugins source path %s' % self.path_ui
        assert isinstance(self.actionWorker, dict), 'Invalid actions workers dictionary %s' % self.actionWorker
        assert isinstance(self.destFolder, str), 'Invalid destination folder for eggs dictionary %s' % self.destFolder
        
    def preparePackage(self, path):
        '''
        Prepares the env for packaging, building, publishing
        '''
        #TODO: extact preparing from Packager and move it here
        
    def preparePluginUI(self, packagePath, packageName):
        '''
        Prepares the ui plugin for packaging, building, publishing.
            - writes setup.py if doesn't exist
            - creates path for mockup folder
            - creates symlink to the source folder
             
        '''
        if not os.path.isdir(packagePath): os.makedirs(packagePath)
        destSymlink = os.path.join(packagePath, packageName)
        sourcePath = os.path.abspath(os.path.join(self.path_ui, packageName))
        os.symlink(sourcePath, destSymlink)
        filename = os.path.join(packagePath, SETUP_FILENAME)
        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                f.write(SETUP_UI_TEMPLATE.format(packageName=packageName))
                f.close()
    
    def process(self): 
        '''
        Process all actions
        '''
        for action, targets in self.actions.items():
            for target in targets:
                if not os.path.isdir(target['path']): os.makedirs(target['path'])
                packagesPaths = getDirs(target['path']) if not target['type']=='plugins-ui' else getDirs(self.path_ui)
                for packageName in packagesPaths:
                    packagePath = os.path.abspath(os.path.join(target['path'], packageName))
                    if target['type']=='plugins-ui': 
                        self.preparePluginUI(packagePath, packageName)
                    assert log.info('*** {name} *** {action} *** STARTED'.format(name=packageName, action=action)) or True
                    worker = self.actionWorker[action](packageName, packagePath)
                    if action == 'package':
                        worker.destFolder = self.destFolder
                    getattr(worker, action)()
                    assert log.info('*** {name} *** {action} *** DONE'.format(name=packageName, action=action)) or True