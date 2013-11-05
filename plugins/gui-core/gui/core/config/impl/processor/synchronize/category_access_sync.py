'''
Created on Oct 28, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Provides the synchronization with the database for accesses.
'''

from functools import reduce

from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor, Handler
import logging
from acl.api.group import IGroupService
from security.api.right import IRightService
from acl.api.acl import IAclPrototype

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Solicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Required
    syncAccesses = requires(list)
    
class SyncAccess(Context):
    # ---------------------------------------------------------------- Required
    #category info
    groupId = requires(str)
    rightId = requires(int)
    categoryName = requires(str)
    
    #access info
    accessId = requires(int)
    url = requires(str)
    method = requires(str)
    filter = requires(str)
    
    #compensates info
    compensates = requires(dict)
    
    #tracking info
    uri = requires(str)
    line = requires(int)
    column = requires(int)

# --------------------------------------------------------------------

@injected
class SynchronizeCategoryAccessHandler(HandlerProcessor):
    '''
    Implementation for a processor that synchronizes the category (groups and rights) 
    accesses in the configuration file with the database.
    '''
    accessRightService = IRightService; wire.entity('accessRightService')
    accessGroupService = IGroupService; wire.entity('accessGroupService')
    
    accessCategoryService = IAclPrototype; wire.entity('accessCategoryService')
    
    def __init__(self):
        super().__init__(SyncAccess=SyncAccess)
    
    def groupByCategory(self, accesses, categoryIdAttr):
        grouped = {}
        for access in accesses:
            categoryId = getattr(access, categoryIdAttr.__name__) 
            if categoryId in grouped: grouped[categoryId].append(access)
            else: grouped[categoryId] = [access]
        
        return grouped
    
    def syncAccessesWithDb(self, syncAccesses):
        for categoryId, accesses in syncAccesses.items():
            self.syncCategoryAccesses(categoryId, accesses)
            
    def syncCategoryAccesses(self, categoryId, accesses):
        accessesFromDb = set(accessId for accessId in self.accessCategoryService.getAccesses(categoryId))
        accessesFromConfig = set(access.accessId for access in accesses)
        
        toAdd = [access for access in accesses if access.accessId in accessesFromConfig.difference(accessesFromDb)]
        toDelete = accessesFromDb.difference(accessesFromConfig)
        
        addedFilters = set(access.filter for access in toAdd if self.addCategoryAccess(categoryId, access) and 
                        self.addAccessFilter(categoryId, access))
        unusedFilters = set(access.filter for access in toAdd if access.filter).difference(addedFilters)
        
        if unusedFilters:
            urls = set([access.url for access in toAdd])
            categoryName, uri, line, column = accesses[0].categoryName, accesses[0].uri, accesses[0].line, accesses[0].column 
            log.warning('Filters (%s) do not apply to any of the access URLs (%s) defined in category \'%s\' in file \'%s\' at line \'%s\' column \'%s\' ',
                        reduce(lambda x, y: '\'%s\',\'%s\'' % (x,y), unusedFilters), 
                        reduce(lambda x, y: '\'%s\',\'%s\'' % (x,y), urls),
                        categoryName, uri, line, column)
        
        for accessId in toDelete: self.accessCategoryService.remAcl(categoryId, accessId)
        
    def addCategoryAccess(self, categoryId, access):
        try:
            self.accessCategoryService.remAcl(categoryId, access.accessId)
            self.accessCategoryService.addAcl(categoryId, access.accessId)
            return True
        except:
            log.warning('Unknown access \'%s\' for method \'%s\' defined in category \'%s\' in file \'%s\' at line \'%s\' column \'%s\' ',
                        access.url, access.method, access.categoryName, access.uri, access.line, access.column)
            return False
    
    def addAccessFilter(self, categoryId, access):
        try:
            if access.filter:
                return self.accessCategoryService.registerFilter(categoryId, access.accessId, access.filter, access.url)
            return False
        except:
            log.warning('Unknown filter \'%s\' in category \'%s\' in file \'%s\' at line \'%s\' column \'%s\'', 
                        access.filter, access.categoryName, access.uri, access.line, access.column)
            return False
    
    
    def syncCompensatesWithDb(self, syncAccesses):
        for categoryId, accesses in syncAccesses.items():
            for access in accesses: self.syncAccessCompensates(categoryId, access)
    
    def syncAccessCompensates(self, category, access):
        '''
        Method to synchronize access compensates from the configuration file with the database.
        '''
        if not access.compensates: return
        
        compensatesDb = set(compensate.Access for compensate in self.accessCategoryService.getCompensates(category, access.accessId))
        compensatesConfig = set(cid for cid in access.compensates.keys())
        
        toAdd = compensatesConfig.difference(compensatesDb)
        toDelete = compensatesDb.difference(compensatesConfig)
        
        for compensateId in toAdd:
            try:
                self.accessCategoryService.addCompensate(category, access.accessId, compensateId)
            except:
                log.warning('Unknown compensate \'%s\' for method \'%s\' defined in category \'%s\' in file \'%s\' at line \'%s\' column \'%s\' ',
                           access.compensates.get(compensateId), access.method, access.categoryName, access.uri, access.line, access.column)
        
        #remove the remaining compensates
        for compensateId in toDelete:
            self.accessCategoryService.remCompensate(category, access.accessId, compensateId)


@injected
@setup(Handler, name='syncGroupAccesses')
class SynchronizeGroupAccessHandler(SynchronizeCategoryAccessHandler):
    '''
    Implementation for a processor that synchronizes the category (groups and rights) 
    accesses in the configuration file with the database.
    '''
    accessCategoryService = IGroupService; wire.entity('accessCategoryService')
    
    def __init__(self):
        assert isinstance(self.accessCategoryService, IGroupService), \
        'Invalid right service %s' % self.accessCategoryService
        super().__init__()
    
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the accesses in the configuration file with the accesses in the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        
        #get the accesses for the groups and group them by groupId
        accesses = [acc for acc in filter(lambda access: access.groupId, solicit.syncAccesses)]
        grouped = self.groupByCategory(accesses, SyncAccess.groupId)
        
        self.syncAccessesWithDb(grouped)
        self.syncCompensatesWithDb(grouped)
        
        
@injected
@setup(Handler, name='syncRightAccesses')
class SynchronizeRightAccessHandler(SynchronizeCategoryAccessHandler):
    '''
    Implementation for a processor that synchronizes the category (groups and rights) 
    accesses in the configuration file with the database.
    '''
    accessCategoryService = IRightService; wire.entity('accessCategoryService')
    
    def __init__(self):
        assert isinstance(self.accessCategoryService, IRightService), \
        'Invalid right service %s' % self.accessCategoryService
        super().__init__()
    
    def process(self, chain, solicit:Solicit, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Synchronize the accesses in the configuration file with the accesses in the database.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        
        #get the accesses for the rights and group them by rightId
        accesses = [acc for acc in filter(lambda access: access.rightId, solicit.syncAccesses)]
        grouped = self.groupByCategory(accesses, SyncAccess.rightId)
        
        self.syncAccessesWithDb(grouped)
        self.syncCompensatesWithDb(grouped)

