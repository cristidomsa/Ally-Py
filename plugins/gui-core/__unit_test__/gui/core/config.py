'''
Created on Aug 22, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

GUI core configuration XML testing.
'''
# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

import logging
import unittest

from ally.support.util_io import IInputStream
from ally.container.ioc import initialize
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, FILL_ALL
from ally.xml.digester import RuleRoot, Node
from gui.core.config.impl.processor.xml.parser import ParserHandler
from gui.core.config.impl.rules import URLRule, ActionRule, MethodRule, \
    AccessRule, GroupRule, DescriptionRule, RightRule
from ally.support.util_context import listBFS

from gui.core.config.impl.processor.synchronize.category import RepositoryGroup, RepositoryRight,\
    SynchronizeRightsHandler

from pkg_resources import get_provider, ResourceManager
# --------------------------------------------------------------------

logging.basicConfig()
logging.getLogger('ally.design.processor').setLevel(logging.INFO)

# --------------------------------------------------------------------
    
class TestSolicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Defined
    stream = defines(IInputStream)
    uri = defines(str)
    # ---------------------------------------------------------------- Required
    repository = requires(Context)

# --------------------------------------------------------------------
    
class TestConfigurationParsing(unittest.TestCase):
    
    def __init__(self, methodName):
        super().__init__(methodName)
        assemblyParsing = self.createAssemplyParsing()
        self.parseResult = self.executeProcess(assemblyParsing)
        
        self.groups = {group.groupName:group for group in 
                       listBFS(self.parseResult.solicit.repository, RepositoryGroup.children, RepositoryGroup.groupName)}
        
        self.rightRepos = listBFS(self.parseResult.solicit.repository, RepositoryGroup.children, RepositoryRight.rightName)
        self.rights = {right.rightName:right for right in self.rightRepos}
        self.rightsInheritance = {right.rightName:[right] for right in self.rightRepos}
        
        self.syncRigthsAssembler = SynchronizeRightsHandler()
    
    def testGroupsRightsNumber(self):
        '''Checks if the number of parsed groups and rights is correct '''
        self.assertTrue(len(self.groups) == 2 and len(self.rights) == 5, 'Wrong number of groups and rights: %s groups, %s rights' \
                                                                        % (len(self.groups), len(self.rights))) 
    
    def testGroupsExist(self):
        '''Checks if Anonymous and Captcha groups have been parsed '''
        self.assertTrue('Anonymous' in self.groups and 'Captcha' in self.groups, 'Missing groups: Anonymous and Captcha')
    
    def testRightsExist(self):
        '''Checks if rights Requests_inspection and Requests_inspection_2 have been parsed'''
        self.assertTrue('Requests_inspection' in self.rights and 'Requests_inspection_2' in self.rights, 'Missing rights: Requests_inspection, Requests_inspection_2')
    
    def testDescription(self):
        '''Checks if description of rights has been parsed '''
        for right in self.rights.values():
            self.assertIsNotNone(right.description, 'Missing description for %s' % right.description)
    
    def testGroupActions(self):
        '''Checks if actions of Anonymous group have been correctly parsed '''
        self.checkActions(self.groups, 'Anonymous', ['menu', 'menu.request', 'menu.request.blob', 'menu.mucu', 'menu.cucu'])
    
    def testRightActions(self):
        '''Checks if actions of Requests_inspection right have been correctly parsed '''
        self.checkActions(self.rights, 'Requests_inspection', ['menu_2', 'menu_2.request', 'menu_2.mucu'])
    
    def testGroupAccesses(self):
        '''Checks if accesses of Anonymous group have been correctly parsed '''
        toCheck = [(filter, url, method) for filter in ['FilterDummy','Authent','lala'] for method in ['GET'] 
                   for url in ['User/*', 'User/*/Blog', 'User/#/SubUser/*']]
        self.checkAccesses(self.groups, 'Anonymous', toCheck)
    
    def testRightAccesses(self):
        '''Checks if accesses of Requests_inspection right have been correctly parsed '''
        toCheck = [(filter, url, method) for filter in ['userAuth'] for method in ['GET'] 
                   for url in ['HR/User/*', 'HR/User/*/Action', 'HR/User/#/SubUser/*']]
        self.checkAccesses(self.rights, 'Requests_inspection', toCheck)
    
    def testRightInheritance(self):
        '''Checks if inheritance attribute was correctly parsed '''
        self.assertTrue('Requests_inspection' in self.rights['Requests_inspection_2'].rightInherits, 'Inheritance not detected for Requests_inspection_2 and Requests_inspection')
    
    def testCyclicInheritance(self):
        '''Checks if cyclic inheritance has been correctly detected '''        
        self.assertTrue(self.syncRigthsAssembler.isCyclicInheritance('Right_1', self.rightsInheritance), 'Cyclic inheritance not detected for %s' % self.rights)
        self.assertFalse(self.syncRigthsAssembler.isCyclicInheritance('Requests_inspection', self.rightsInheritance), 'Non-existing cyclic inheritance detected for Requests_inspection')
    
    def testInheritanceForActions(self):
        '''Checks if actions have been correctly inherited for rights'''
        cyclicInheritance = ['Right_1', 'Right_2', 'Right_3']
        self.syncRigthsAssembler.doInheritance([right for right in self.rightRepos if right.rightName not in cyclicInheritance])
        self.checkActions(self.rights, 'Requests_inspection_2', ['menu_2', 'menu_2.request', 'menu_2.mucu'])
    
    def testInheritanceForAccesses(self):
        '''Checks if accesses have been correctly inherited for rights'''
        cyclicInheritance = ['Right_1', 'Right_2', 'Right_3']
        self.syncRigthsAssembler.doInheritance([right for right in self.rightRepos if right.rightName not in cyclicInheritance])
        toCheck = [(filter, url, method) for filter in ['userAuth'] for method in ['GET'] 
                   for url in ['HR/User/*', 'HR/User/*/Action', 'HR/User/#/SubUser/*']]
        self.checkAccesses(self.rights, 'Requests_inspection_2', toCheck)
    
    def checkAccesses(self, categories, categoryName, toCheck):
        filtersUrlsMethods = set((filter, url.url, method) for access in categories[categoryName].accesses for url in access.urls 
                       for method in access.methods for filter in access.filters)
        missing = []
        for t in toCheck:
            if not t in filtersUrlsMethods: missing.append(t)
        self.assertFalse(missing, 'Missing accesses from category %s: %s' % (categoryName, missing)) 
    
    def checkActions(self, categories, categoryName, toCheck):
        actions = {action.path: action for action in categories[categoryName].actions}
        missing = []
        for action in toCheck:
            if not action in actions: missing.append(action)
        self.assertFalse(missing, 'Missing actions from category %s: %s' % (categoryName, missing))
    
    def executeProcess(self, assembly):
        proc = assembly.create(solicit=TestSolicit)
        assert isinstance(proc, Processing)
        
        #use packageProvider (not os package) to access files from inside the package (like config_test.xml)
        packageProvider = get_provider(__name__)
        manager = ResourceManager()
        self.assertTrue(packageProvider.has_resource('config_test.xml'), 'Xml Config file missing')
        
        content = packageProvider.get_resource_stream(manager, 'config_test.xml')
        solicit = proc.ctx.solicit(stream=content, uri = 'file://%s' % 'config_test.xml')
        
        arg = proc.execute(FILL_ALL, solicit=solicit)
        assert isinstance(arg.solicit, TestSolicit)
        content.close()
        return arg
    
    def createAssemplyParsing(self):
        parser = ParserHandler()
        parser.rootNode = RuleRoot()
        
        anonymous = parser.rootNode.addRule(GroupRule(), 'Config/Anonymous')
        captcha = parser.rootNode.addRule(GroupRule(), 'Config/Captcha')
        right = parser.rootNode.addRule(RightRule('name', 'inherits'), 'Config/Right')
        right.addRule(DescriptionRule(), 'Description')
        
        #allows = anonymous.addRule(AccessRule(), 'Allows')
        allows = Node('Allows')
        allows.addRule(AccessRule())
        #allows.addRule(MethodRule(fromAttributes=True))
        allows.addRule(URLRule(), 'URL')
        allows.addRule(MethodRule(), 'Method')
        
        action = Node('Action')
        action.addRule(ActionRule())
        action.childrens['Action'] = action
        
        actions = Node('Actions')
        actions.childrens['Action'] = action
        
        anonymous.childrens['Actions'] = actions
        anonymous.childrens['Action'] = action
        anonymous.childrens['Allows'] = allows
        
        #no actions for captcha
        captcha.childrens['Allows'] = allows
        
        right.childrens['Actions'] = actions
        right.childrens['Action'] = action
        right.childrens['Allows'] = allows
        
        assemblyParsing = Assembly('Parsing XML')
        assemblyParsing.add(initialize(parser))
        return assemblyParsing
    
# --------------------------------------------------------------------

if __name__ == '__main__': unittest.main()