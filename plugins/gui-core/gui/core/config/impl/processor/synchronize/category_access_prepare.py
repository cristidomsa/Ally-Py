'''
Created on Oct 9, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Prepares the synchronization with the database for accesses.
'''

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor, Handler
from ally.support.util_context import listBFS, hasAttribute
import logging
from acl.api.access import generateId

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Solicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Defines
    syncAccesses = defines(list)
    
    # ---------------------------------------------------------------- Required
    repository = requires(Context)

class Repository(Context):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Required
    children = requires(list)
    accesses = requires(list)

class SyncAccess(Context):
    # ---------------------------------------------------------------- Defines
    #category info
    groupId = defines(str)
    rightId = defines(int)
    categoryName = defines(str)
    
    #access info
    accessId = defines(int)
    url = defines(str)
    method = defines(str)
    filter = defines(str)
    
    #compensates info
    compensates = defines(dict)
    
    #tracking info
    uri = defines(str)
    line = defines(int)
    column = defines(int)


class Access(Context):
    '''
    The access container context.
    '''
    # ---------------------------------------------------------------- Required
    filters = requires(list)
    methods = requires(list)
    urls = requires(list)
    lineNumber = requires(int)
    colNumber = requires(int)
    uri = requires(str)

class URL(Context):
    # ---------------------------------------------------------------- Required
    url = requires(str)
    compensates = requires(list)

# --------------------------------------------------------------------

@injected
class PrepareCategoryAccessHandler(HandlerProcessor):
    '''
    Base implementation for a processor that synchronizes the accesses in the configuration file with the database.
    '''
    
    default_access_methods = ['GET']; wire.config('default_access_methods', doc='''
    The default access methods (will be used if no methods are provided for an access). 
    ''')
    
    def __init__(self, Repository):
        super().__init__(Repository=Repository, Access=Access, URL=URL, SyncAccess=SyncAccess)
    
    def createSyncAccesses(self, SyncAccess, entityAccesses, entityIdNameMapping=None, isRight=False):
        if entityIdNameMapping is None: entityIdNameMapping = {}
        return [acc for entityId, accesses in entityAccesses.items() 
                for acc in self.filterSyncAccesses(self.categorySyncAccesses(SyncAccess, entityId, 
                                                                             entityIdNameMapping.get(entityId, entityId), 
                                                                             isRight, accesses))]
    
    def categorySyncAccesses(self, SyncAccess, categoryId, categoryName, isRight, accesses):
        if not accesses: return []
        return [self.createSyncAccess(SyncAccess, categoryId, categoryName, isRight, filter, url, method, compensates, 
                                          (access.uri, access.lineNumber, access.colNumber))
                    for access in accesses
                    for filter,url,method,compensates in self.getFiltersUrlsMethods(access)]
        
    def createSyncAccess(self,SyncAccess, categoryId, categoryName, isRight, filter, url, method, compensates, trackingInfo):
        accessId = generateId(url.strip('/').replace('#', '*'), method)
        if compensates:
            compensateIds = {generateId(compensate.strip('/').replace('#', '*'), method):compensate for compensate in compensates}
        else: compensateIds = None
        
        access = SyncAccess()
        assert isinstance(access, SyncAccess), 'Invalid sync access context %s' % access
        if isRight: access.rightId = categoryId
        else: access.groupId = categoryId
        access.categoryName = categoryName
        access.accessId = accessId
        access.url = url; access.method = method; access.filter = filter
        access.compensates = compensateIds
        uri, line, column = trackingInfo
        access.uri = uri; access.line = line; access.column = column
        return access
    
    def getFiltersUrlsMethods(self, access):
        assert isinstance(access, Access), 'Invalid access context %s' % access
            
        if not access.urls: return []
        if not access.methods: access.methods = self.default_access_methods
        
        filters = access.filters if access.filters else [None]
        #a list of tuples containing all combinations of filters, methods and urls
        return [(filter, url.url, method, url.compensates) for filter in filters for url in access.urls 
                for method in access.methods]
    
    def groupAccesses(self, repositories, Repository, idAttr):
        '''
        For a list of repositories, groups the accesses by some Id attribute.
        @return: mapping Id : list of actions
        '''
        groupAccesses = {}
        for repository in repositories:
            assert isinstance(repository, Repository), 'Invalid repository %s' % repository
            assert hasAttribute(Repository, idAttr.__name__), 'Invalid repository %s' % repository
            accesses = groupAccesses.get(getattr(repository, idAttr.__name__))
            if not accesses: groupAccesses[getattr(repository, idAttr.__name__)] = repository.accesses
            else: accesses.extend(repository.accesses)
        
        return groupAccesses

    def filterSyncAccesses(self, accesses):
        '''
        Will discard duplicates (comparing accessId attribute) from a list of SyncAccess contexts 
        '''
        filtered = []
        existing = set()
        for access in accesses:
            if access.accessId in existing: continue
            filtered.append(access)
            existing.add(access.accessId)
            
        return filtered
    

class RepositoryGroup(Repository):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Required
    groupName = requires(str)
    
@injected
@setup(Handler, name='prepareGroupAccesses')
class PrepareGroupAccessHandler(PrepareCategoryAccessHandler):
    '''
    Implementation for a processor that synchronizes the group accesses in the configuration file with the database.
    '''
    
    def __init__(self):
        super().__init__(RepositoryGroup)
        
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the group accesses in the configuration file with the accesses in the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert isinstance(solicit.repository, RepositoryGroup), 'Invalid repository %s' % solicit.repository
        
        groups = listBFS(solicit.repository, RepositoryGroup.children, RepositoryGroup.groupName)
        #first group the accesses by group name: groupName -> [accesses]
        groupAccesses = self.groupAccesses(groups, RepositoryGroup, RepositoryGroup.groupName)
        
        if not solicit.syncAccesses: solicit.syncAccesses = []
        solicit.syncAccesses.extend(self.createSyncAccesses(chain.arg.SyncAccess, groupAccesses))


class RepositoryRight(Repository):
    '''
    The repository context.
    '''
    # ---------------------------------------------------------------- Required
    rightName = requires(str)
    rightId = requires(int)

@injected
@setup(Handler, name='prepareRightAccesses')
class PrepareRightAccessHandler(PrepareCategoryAccessHandler):
    '''
    Implementation for a processor that synchronizes the right accesses in the configuration file with the database.
    '''
    
    def __init__(self):
        super().__init__(RepositoryRight)
        
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the accesses in the configuration file with the accesses in the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        assert isinstance(solicit.repository, RepositoryRight), 'Invalid repository %s' % solicit.repository
        
        rights = listBFS(solicit.repository, RepositoryRight.children, RepositoryRight.rightId)
        #first group the accesses by right id: rightId -> [accesses]
        idNameMapping = self.getIdNameMapping(rights, RepositoryRight, RepositoryRight.rightId, RepositoryRight.rightName)
        rightAccesses = self.groupAccesses(rights, RepositoryRight, RepositoryRight.rightId)
        
        if not solicit.syncAccesses: solicit.syncAccesses = []
        solicit.syncAccesses.extend(self.createSyncAccesses(chain.arg.SyncAccess, rightAccesses, idNameMapping, True))
        
    def getIdNameMapping(self, repositories, Repository, idAttr, nameAttr):
        '''
        Creates mapping rightId : rightName for the given repositories. 
        '''
        idNameMapping = {}
        for repository in repositories:
            assert isinstance(repository, Repository), 'Invalid repository %s' % repository
            assert hasAttribute(Repository, idAttr.__name__), 'Invalid repository %s' % repository
            assert hasAttribute(Repository, nameAttr.__name__), 'Invalid repository %s' % repository
            idNameMapping[getattr(repository, idAttr.__name__)] = getattr(repository, nameAttr.__name__)
        
        return idNameMapping
        
    