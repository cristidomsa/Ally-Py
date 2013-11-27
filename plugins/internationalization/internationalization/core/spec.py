'''
Created on Mar 13, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for PO file management.
'''

import abc

# --------------------------------------------------------------------

class InvalidLocaleError(Exception):
    '''
    Raise whenever there is a invalid locale provided.
    '''

# --------------------------------------------------------------------

class ICatalogManager(metaclass=abc.ABCMeta):
    '''
    The PO file manager: processes and returns the global or plugin
    PO/POT files content from anywhere.
    '''
        
    @abc.abstractmethod
    def getGlobalPOCatalog(self, locale):
        '''
        Provides the global messages catalog for the given locale.
        

        @param locale: string
            The locale for which to return the translation.
        @return: catalog
            The PO file catalog containing the translation.
        '''
    
    @abc.abstractmethod
    def getPluginPOCatalog(self, name, locale):
        '''
        Provides the messages catalog for the specified plugin and the given locale.

        @param locale: string
            The locale for which to return the translation.
        @return: catalog
            The PO file catalog containing the translation.
        '''

    @abc.abstractmethod
    def getGlobalPOTCatalog(self):
        '''
        Provides the POT file messages catalog for the whole application
        
        @return: catalog
            The global POT file catalog.
        '''
    
    @abc.abstractmethod
    def getPluginPOTCatalog(self, name):
        '''
        Provides the POT file messages catalog for the specified plugin
        
        @param name: string
            The name of the plugin for which the POT file is needed.
        @return: catalog
            The PO file catalog containing the translations for the specified plugin.
        '''

    @abc.abstractmethod
    def updateGlobalPO(self, locale, poFile):
        '''
        Updates the global PO file for the provided locale. 
        
        @param locale: string
            The locale for which to return translation
        '''
    
    @abc.abstractmethod
    def updatePluginPO(self, name, locale, poFile):
        '''
        Updates the plugin PO file for the provided locale. 
        
        @param locale: string
            The locale for which to return translation
        '''
    
    @abc.abstractmethod
    def updatePluginPOT(self, name, potFile):
        '''
        Updates the plugin POT file. 
        
        @param locale: string
            The locale for which to return translation
        '''

class ICDMSyncronizer(metaclass=abc.ABCMeta):
    '''
    CDM syncronization
    '''
    
    @abc.abstractmethod
    def publish(self, content, name, locale, timestamp):
        '''
        Publishes content to the CDM
        
        @param content: Catalog
        @param name: string
        @param name: string
        '''
    @abc.abstractmethod
    def asReference(self, path, protocol):
        '''
        returns path as reference
        '''