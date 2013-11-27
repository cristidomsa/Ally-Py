'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Implementation for the PO file management.
'''

from ally.api.model import Content
from ally.container import wire
from ally.container.ioc import injected
from ally.container.support import setup
from ally.core.error import DevelError
from ally.api.error import InputError, IdError
from ally.internationalization import _, C_
from internationalization.api.po_file import IInternationlizationFileService
from internationalization.core.spec import IPOFileManager, InvalidLocaleError,\
    ICDMSyncronizer
from babel.core import Locale, UnknownLocaleError
import logging
from ..internationalization.service import globalMessagesName

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------
@injected
@setup(IInternationlizationFileService, name='poFileService')
class POFileService(IInternationlizationFileService):
    '''
    Implementation for @see: IInternationlizationFileService
    '''

    poFileManager = IPOFileManager; wire.entity('poFileManager')
    cdmSync = ICDMSyncronizer; wire.entity('cdmSync')

    def __init__(self):
        assert isinstance(self.poFileManager, IPOFileManager), 'Invalid PO file manager %s' % self.poFileManager
        assert isinstance(self.cdmSync, ICDMSyncronizer), 'Invalid CDM syncronizer %s' % self.cdmSync
        
    def getPOFile(self, locale, scheme, name=None):
        '''
        @see: IInternationlizationFileService.getPOFile
        '''
        try: Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        if not name:
            result = self.poFileManager.getGlobalPOCatalog(locale, scheme)
            timestamp = self.poFileManager.getLatestTimestampForPO(name=globalMessagesName(), locale=locale)
            if not result: raise IdError('No global PO file available. Upload one before trying to get one!')
            else: timestamp = self.poFileManager.getLatestTimestampForPO(name=globalMessagesName(), locale=locale)
        else:
            result = self.poFileManager.getPluginPOCatalog(name, locale)
            if not result:
                assert log.debug('No PO file for plugin {name}, trying to get global PO...'.format(name=name)) or True 
                result = self.poFileManager.getGlobalPOCatalog(locale)
                if not result:
                    raise IdError('No global PO file available. Upload one before trying to get one!')
                else: timestamp = self.poFileManager.getLatestTimestampForPO(name=globalMessagesName(), locale=locale)
            else:
                timestamp = self.poFileManager.getLatestTimestampForPO(name=name, locale=locale)
        path = self.cdmSync.publish(result, name, locale,  timestamp)
        return self.cdmSync.asReference(path, scheme)

    def getPOTFile(self, scheme, name=None):
        '''
        @see: IInternationlizationFileService.getPOTFile
        '''
        if not name:
            result = self.poFileManager.getGlobalPOTCatalog()
            if not result: raise IdError('No global POT file could be generated!')
            else: timestamp = self.poFileManager.getLatestTimestampForPOT(name=globalMessagesName())
            name = globalMessagesName()
        else:
            result = self.poFileManager.getPluginPOTCatalog(name)
            timestamp = self.poFileManager.getLatestTimestampForPOT(name)
            if not result: raise IdError('No POT file available for plugin {name}. Upload one before trying to get one!'.format(name=name))
            else: timestamp = self.poFileManager.getLatestTimestampForPOT(name)
        path = self.cdmSync.publish(result, name, locale=None, timestamp=timestamp)
        return self.cdmSync.asReference(path, scheme)

    def updatePOFile(self, locale, poFile, name=None):
        '''
        @see: IInternationlizationFileService.updatePOFile
        '''
        try: Locale.parse(locale)
        except UnknownLocaleError: raise InvalidLocaleError(locale)
        assert isinstance(poFile, Content), 'Invalid PO content %s' % poFile
        if name:
            try:
                result = self.poFileManager.updatePluginPO(name=name, locale=locale, poFile=poFile)
            except UnicodeDecodeError: raise InvalidPOFile(poFile)
        else:
            try:
                result = self.poFileManager.updateGlobalPO(locale=locale, poFile=poFile)
            except UnicodeDecodeError: raise InvalidPOFile(poFile)
        if poFile.next(): raise ToManyFiles()
        return result

        
    def insertPOTFile(self, name, poFile):
        '''
        @see: IInternationlizationFileService.insertPOTFile
        '''
        assert isinstance(poFile, Content), 'Invalid PO content %s' % poFile
        try: result = self.poFileManager.updatePluginPOT(name=name, poFile=poFile)
        except UnicodeDecodeError: raise InvalidPOFile(poFile)
        if poFile.next(): raise ToManyFiles()
        return result

    # ----------------------------------------------------------------
    
# Raised when there is an invalid PO content
InvalidPOFile = lambda poFile:InputError(_('Invalid content for PO file %(file)s') % dict(file=poFile.getName() or
                                                                                    C_('Unknown file name', 'unknown')))

# Raised if there are to many files provided in content.
ToManyFiles = lambda :DevelError('To many PO files, only one accepted')
