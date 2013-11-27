'''
Created on Mar 9, 2012

@package: internationalization
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

API specifications for PO file management.
'''

from ally.api.config import service, call, model
from ally.api.model import Content
from ally.api.type import Scheme, Reference
from internationalization.api.domain import modelLocalization
from internationalization.language.api.language import Language

# --------------------------------------------------------------------

@modelLocalization(id='Name')
class PO:
    '''
    Model for a PO file.
    '''
    Name = str
    Reference = Reference
    
# --------------------------------------------------------------------

@service
class IInternationlizationFileService:
    '''
    The PO/POT file management service.
    '''
    @call(webName='Messages')
    def getPOFile(self, locale:Language.Code, scheme:Scheme, name:PO.Name=None) -> PO.Reference:
        '''
        Provides the PO file for the plugin and the given locale. If name is None, global PO file will be provided.

        
        @param locale: Language.Code
            The locale for which to return the translation.
        @param name: string
            The name of the plugin
        @return: Reference
            The reference to the content of the PO file.
        '''

    @call(webName='Messages')
    def updatePOFile(self, locale:Language.Code, content:Content, name:PO.Name=None) -> bool:
        '''
        Update a PO file for specified locale or upload new locale if doesn't exist. If name is None, file will be uploaded a global PO file.
        
        @param locale: Language.Code
            The locale for which to return the translation.
        @param name: string
            The name of the plugin
        '''
                
    # ----------------------------------------------------------------
    
    @call(webName='Template')
    def getPOTFile(self, scheme:Scheme, name:PO.Name=None) -> PO.Reference:
        '''
        Provides the POT file for the specified plugin. If name is None the global POT file will be provided.
    
        @param name: string
            The name of the plugin
        @return: Reference
            The reference to the content of the POT file.
        '''
    
    @call(webName='Template')
    def insertPOTFile(self, name:PO.Name, content: Content) -> bool:
        '''
        Insert a POT file for the specified plugin, overwrite if exists.
        
        @param name: string
            The name of the plugin
        '''