'''
Created on Mar 13, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from ally.container.ioc import injected
from ally.container.support import setup
from internationalization.core.spec import ICatalogManager
import logging
from internationalization.core.impl.catalog_manager import CatalogManager
from sql_alchemy.support.util_service import SessionSupport
from internationalization.meta.db_mapping import POTMapped, POMapped
from sqlalchemy.sql.expression import and_
from datetime import datetime
from ..internationalization.service import globalMessagesName

# --------------------------------------------------------------------

log = logging.getLogger(__name__)
# --------------------------------------------------------------------

@injected
@setup(ICatalogManager, name='dbPOFileManager')
class DBPOFileManager(CatalogManager, SessionSupport):
    '''
    Implementation for @see: IPOFileManager
    '''
    
    def __init__(self):
        '''
        Construct
        '''
        
    def getData(self, name, locale=None):
        
        '''
        gets data from localization db
        
        @param name: string 
            The name of the plugin
        @param locale: string 
            The locale for which the data is needed
        @return binary data
            The PO/POT file as binary data
        '''
        
        if not locale:
            sql = self.session().query(POTMapped)
            sql = sql.filter(POTMapped.Name == name)
        else:
            sql = self.session().query(POMapped)
            sql = sql.filter(and_(POMapped.Name == name, POMapped.Locale == locale))
        
        result = sql.first()
        if result:
            return result.file
        else:
            assert log.debug('No result found for name \'%s\' and locale \'%s\'', name, locale) or True
            return False
            
    def storeData(self, content, name, locale=None):
        '''
        stores data in localization db
        
        @param name: string 
            The name of the plugin
        @param locale: string 
            The locale for which the data is needed
        @return boolean
            True if success, False if not
        '''
        
        timestamp = int(datetime.now().strftime('%s'))
        if not locale:
            sql = self.session().query(POTMapped)
            sql = sql.filter(POTMapped.Name == name)
        else:
            sql = self.session().query(POMapped)
            sql = sql.filter(and_(POMapped.Name == name, POMapped.Locale == locale))
        
        item = sql.first()
        if item:
            item.timestamp = timestamp
            item.file = content
        else:
            item = POMapped(Name=name, Locale=locale, timestamp=timestamp, file=content) if locale \
                   else POTMapped(Name=name, timestamp=timestamp, file=content) 
            assert log.debug('Entry does not exist. Adding new entry') or True
        try:
            self.session().add(item)
            return True
        except:
            assert log.debug('Storing PO in db failed!', exc_info=1) or True
            return False
        
    def getAllPOTs(self):
        '''
        Returns the list of all POT files from db
        
        @return list
            The list of pots stored in db
        '''
        
        return self.session().query(POTMapped.Name).all()
    
    def getLatestTimestampForPOT(self, name):
        '''
        Implementaion for @see: CatalogManager.getLatestTimestampForPOT
        '''
        if name == globalMessagesName():
            return int(datetime.now().strftime('%s'))
        
        sql = self.session().query(POTMapped.timestamp)
        sql = sql.filter(POTMapped.Name == name)
        
        result = sql.first()
        if result:
            return result.timestamp
        else:
            assert log.debug('No POT for {name}, no timestamp could be found'.format(name=name)) or True
            return False
            
    def getLatestTimestampForPO(self, name, locale):
        '''
        Implementaion for @see: CatalogManager.getLatestTimestampForPO
        '''
        
        sql = self.session().query(POMapped.timestamp)
        sql = sql.filter(and_(POMapped.Name == name, POMapped.Locale == locale))
        
        resultPO = sql.first()
        if resultPO:
            timestampPOT = self.getLatestTimestampForPOT(name)
            if timestampPOT:
                timestamp = timestampPOT if timestampPOT > resultPO.timestamp else resultPO.timestamp
            else:
                timestamp = resultPO.timestamp
            return timestamp
        else:
            assert log.debug('No PO for {name} and {locale}, no timestamp could be found'.format(name=name, locale=locale)) or True
            return False