'''
Created on Jan 9, 2012

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains the services for the gui core.
'''

from __setup__.ally.notifier import registersListeners
from ally.container import ioc, support
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
from ally.xml.digester import Node, RuleRoot
from gui.core.config.impl.processor.configuration_notifier import \
    ConfigurationListeners
from gui.core.config.impl.processor.xml.parser import ParserHandler
from gui.core.config.impl.rules import AccessRule, MethodRule, URLRule, \
    ActionRule, DescriptionRule, GroupRule, RightRule

# --------------------------------------------------------------------
# The synchronization processors
synchronizeAction = synchronizeGroups = synchronizeRights = synchronizeGroupActions = synchronizeRightActions =\
prepareGroupAccesses = prepareRightAccesses = syncCategoryAccesses = syncGroupAccesses = syncRightAccesses = support.notCreated  # Just to avoid errors
support.createEntitySetup('gui.core.config.impl.processor.synchronize.**.*')

# --------------------------------------------------------------------

@ioc.config
def access_group():
    '''
    Contains the names of the access groups that are expected in the configuration file. Expected properties are name and
    optionally a flag indicating if actions are allowed.
    '''
    return {
            'Anonymous': dict(hasActions=True, isAnonymous=True),
            'Captcha': dict(hasActions=False),
            'Right': dict(hasActions=True, isRight=True)
            }
    
@ioc.config
def gui_configuration():
    ''' The URI pattern (can have * for dynamic path elements) where the XML configurations can be found.'''
    return ['file://../superdesk/plugins-ui/*/config.xml', 'file://../superdesk/plugins-ui/superdesk/user/config.xml']

# --------------------------------------------------------------------

@ioc.entity
def assemblyConfiguration() -> Assembly:
    return Assembly('GUI Configurations')

@ioc.entity
def nodeRootXML() -> Node: return RuleRoot()

@ioc.entity
def parserXML() -> Handler:
    b = ParserHandler()
    b.rootNode = nodeRootXML()
    return b

@ioc.entity
def configurationListeners() -> Handler:
    b = ConfigurationListeners()
    b.assemblyConfiguration = assemblyConfiguration()
    b.patterns = gui_configuration()
    return b

# --------------------------------------------------------------------

@ioc.before(synchronizeGroupActions)
def updateAccessGroup():
    synchronizeGroupActions().anonymousGroups = set(name for name, spec in access_group().items()
                                                    if spec.get('isAnonymous', False))

@ioc.before(synchronizeGroups)
def updateGroup():
    synchronizeGroups().anonymousGroups = set(name for name, spec in access_group().items()
                                                    if spec.get('isAnonymous', False))

@ioc.before(nodeRootXML)
def updateRootNodeXMLForGroups():
    for name, spec in access_group().items():
        assert isinstance(name, str), 'Invalid name %s' % name
        assert isinstance(spec, dict), 'Invalid specifications %s' % spec
        if spec.get('isRight', False): node = nodeRootXML().addRule(RightRule('name', 'inherits'), 'Config/%s' % name)
        else: node = nodeRootXML().addRule(GroupRule(), 'Config/%s' % name)
        addNodeAccess(node)
        addNodeDescription(node)
        if spec.get('hasActions', False): addNodeAction(node)

@ioc.before(assemblyConfiguration)
def updateAssemblyConfiguration():
    assemblyConfiguration().add(parserXML(), synchronizeAction(), synchronizeGroups(), synchronizeRights(), 
                                synchronizeGroupActions(), synchronizeRightActions(), 
                                prepareGroupAccesses(), prepareRightAccesses(), syncGroupAccesses(), syncRightAccesses())

@ioc.before(registersListeners)
def updateRegistersListenersForConfiguration():
    registersListeners().append(configurationListeners())

# --------------------------------------------------------------------

def addNodeDescription(node):
    assert isinstance(node, Node), 'Invalid node %s' % node
    node.addRule(DescriptionRule(), 'Description')

def addNodeAccess(node):
    assert isinstance(node, Node), 'Invalid node %s' % node
    
    access = node.addRule(AccessRule(), 'Allows')
    access.addRule(MethodRule(fromAttributes=True))
    access.addRule(URLRule(), 'URL')
    access.addRule(MethodRule(), 'Method')

def addNodeAction(node):
    assert isinstance(node, Node), 'Invalid node %s' % node
    
    action = Node('Action')
    action.addRule(ActionRule())
    action.childrens['Action'] = action
    
    actions = Node('Actions')
    actions.childrens['Action'] = action
    
    node.childrens['Actions'] = actions
    node.childrens['Action'] = action
