'''
Created on Sept 04, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Provides the synchronization with the database for groups.
'''

from acl.api.group import IGroupService, Group
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires, optional, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import Handler, HandlerProcessor
import logging
from ally.support.util_context import listBFS
from security.api.right_type import IRightTypeService
from security.api.right import IRightService, Right, RightType
from functools import partial

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
class Solicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Required
    repository = requires(Context)
    
class Repository(Context):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Required
    children = requires(list)
    lineNumber = requires(int)
    colNumber = requires(int)
    uri = requires(str)

# --------------------------------------------------------------------

class RepositoryGroup(Repository):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Required
    groupName = requires(str)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='synchronizeGroups')
class SynchronizeGroupsHandler(HandlerProcessor):
    '''
    Implementation for a processor that synchronizes the groups in the configuration file with the database.
    '''
    
    groupService = IGroupService; wire.entity('groupService')
    
    anonymousGroups = set
    # The set with the anonymous groups names
    
    def __init__(self):
        assert isinstance(self.groupService, IGroupService)
        'Invalid group service %s' % self.groupService
        assert isinstance(self.anonymousGroups, set), 'Invalid anonymous groups %s' % self.anonymousGroups
        super().__init__(Repository=RepositoryGroup)
        
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the groups of the groups in the configuration file with the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert isinstance(solicit.repository, RepositoryGroup), 'Invalid repository %s' % solicit.repository
        
        #maps name to id
        groupsDb = {name:name for name in self.groupService.getAll()}
        #maps group_name to arguments required for group creation (None for groups)
        groups = {r.groupName: (self.createEntity, r) for r in listBFS(solicit.repository, 
                                                                 RepositoryGroup.children, RepositoryGroup.groupName)}
        syncWithDatabase(self.groupService, groups, groupsDb)
    
    def createEntity(self, groupName):
        group = Group()
        group.Name = groupName 
        group.IsAnonymous = groupName in self.anonymousGroups
        return group

# --------------------------------------------------------------------

class RepositoryRight(Repository):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Defines
    rightId = defines(int)
    # ---------------------------------------------------------------- Optional
    description = optional(str)
    # ---------------------------------------------------------------- Required
    rightName = requires(str)

# --------------------------------------------------------------------
    
@injected
@setup(Handler, name='synchronizeRights')
class SynchronizeRightsHandler(HandlerProcessor):
    '''
    Implementation for a processor that synchronizes the rights in the configuration file with the database.
    '''
    
    type_name = 'GUI Access'; wire.config('type_name', doc='''
    The right type name to be used in inserting the configured rights. 
    ''')
    rightService = IRightService; wire.entity('rightService')
    rightTypeService = IRightTypeService; wire.entity('rightTypeService')
    
    def __init__(self):
        assert isinstance(self.type_name, str), 'Invalid type name %s' % self.type_name
        assert isinstance(self.rightService, IRightService), 'Invalid right service %s' % self.rightService
        assert isinstance(self.rightTypeService, IRightTypeService), 'Invalid right type service %s' % self.rightTypeService
        super().__init__(Repository=RepositoryRight)
        
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the rights of the groups in the configuration file with the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert isinstance(solicit.repository, RepositoryRight), 'Invalid repository %s' % solicit.repository
        
        try: self.rightTypeService.getById(self.type_name)
        except:
            rightType = RightType()
            rightType.Name = self.type_name
            self.rightTypeService.insert(rightType)
        
        #maps name to id
        rightsDb = {e.Name: e.Id for e in [self.rightService.getById(id) for id in self.rightService.getAll(self.type_name)]}
        #maps right_name to arguments required for right creation
        rightRepositories = listBFS(solicit.repository, RepositoryRight.children, RepositoryRight.rightName)
        rights = {r.rightName: (partial(self.createEntity, r), r) for r in rightRepositories}
        rightIds = syncWithDatabase(self.rightService, rights, rightsDb)
        
        #add id to right repositories
        for r in rightRepositories:
            r.rightId = rightIds.get(r.rightName)
    
    def createEntity(self, rightRepository, rightName):
        assert isinstance(rightRepository, RepositoryRight), 'Invalid repository %s' % rightRepository
        right = Right()
        right.Name = rightName
        right.Type = self.type_name
        right.Description = rightRepository.description
        return right

# --------------------------------------------------------------------

def syncWithDatabase(service, entitiesConfig, entitiesDb):
    '''Generic method to synchronize entities (groups and rights) from configuration file with the database.
    
    @param service: the service for the entity to be synchronized
    @type service: IAclPrototype 
    @param entitiesConfig: mapping entityName : entityCreator
    @param entitiesDb: mapping entityName : entityId
    '''
    assert isinstance(entitiesDb, dict), 'Invalid entities mapping %s' % entitiesDb
    assert isinstance(entitiesConfig, dict), 'Invalid entities mapping %s' % entitiesConfig
    
    #will store the name:id mapping of the old and newly created entities
    entityIds = {}
    for entityName, (creator, repository) in entitiesConfig.items():
        if not entityName in entitiesDb:
            assert isinstance(repository, Repository), 'Invalid repository %s' % repository 
            entity = creator(entityName)
            try:
                entityIds[entityName] = service.insert(entity)
            except Exception as e:
                log.warning('Error adding \'%s\' to database in file \'%s\' at line \'%s\', column \'%s\' ', 
                            entity, repository.uri, repository.lineNumber, repository.colNumber)
                log.warning(e)
        else: entityIds[entityName] = entitiesDb.pop(entityName)
    
    # remove the remaining entities that are only in the db and not in the configuration file
    for entityId in entitiesDb.values(): service.delete(entityId)
    return entityIds