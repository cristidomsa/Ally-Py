'''
Created on Nov 13, 2013
   
@package: internationalization
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
   
CDM syncronyzer for the internationlization PO files.
'''
import logging
from ally.container.ioc import injected
from internationalization.core.spec import ICDMSyncronizer
from ally.container.support import setup
from ally.cdm.spec import ICDM
from ally.container import wire
from os.path import join
from babel.compat import BytesIO
from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po
  
# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------



# --------------------------------------------------------------------

@injected
@setup(ICDMSyncronizer, name='poCDMSync')
class POCDMSyncronyzer(ICDMSyncronizer):
    '''
    Implementaion for @see: ICDMSyncronizer
    '''
    cdmLocale = ICDM; wire.entity('cdmLocale')
    
    filename_po = 'messages.po'; wire.config('filename_po', doc='''Filename of PO file in CDM''')
    # The format of the po files.
    
    filename_pot = 'messages.pot'; wire.config('filename_pot', doc='''Filename of POT file in CDM''')
    # The format of the pot files. 
    
    #TODO: get rid of this from here
    write_po_config = {
                       'no_location': False,
                       'omit_header': False,
                       'sort_output': True,
                       'sort_by_file': True,
                       'ignore_obsolete': True,
                       'include_previous': False,
                       }; wire.config('write_po_config', doc='''
    The configurations used when writing the PO files.

    :param width: the maximum line width for the generated output; use `None`, 0, or a negative number to
                  completely disable line wrapping
    :param no_location: do not emit a location comment for every message
    :param omit_header: do not include the ``msgid ""`` entry at the top of the output
    :param sort_output: whether to sort the messages in the output by msgid
    :param sort_by_file: whether to sort the messages in the output by their locations
    :param ignore_obsolete: whether to ignore obsolete messages and not include them in the output; by default
                            they are included as comments
    :param include_previous: include the old msgid as a comment when updating the catalog
    ''')
    
    cdm_po_file_path = join('{name}', 'locale', '{locale}', 'LC_MESSAGES', filename_po); wire.config('cdm_po_file_path', doc='''
    The CDM path for PO files''')
    cdm_pot_file_path = join('{name}', 'locale', filename_pot); wire.config('cdm_pot_file_path', doc='''
    The CDM path for POT files''')
    
    def __init__(self):
        '''
        '''
        
    def publish(self, content, name, locale, timestamp):
        '''
        Publish content to path in CDM if content changed
        '''
        if locale:
            path = self.cdm_po_file_path.format(name=name, locale=locale)
        else:
            path = self.cdm_pot_file_path.format(name=name)
        cdmMetadata = self.cdmLocale.getMetadata(path)
        cdmTimestamp = -1 if not cdmMetadata else cdmMetadata['timestamp']
        if timestamp > cdmTimestamp:
            self.cdmLocale.publishFromFile(path, self._toPOFile(content))
            dbMetadata = {'timestamp': timestamp}
            self.cdmLocale.updateMetadata(path, dbMetadata)
        return path
          
    def asReference(self, path, protocol):
        '''
        returns reference to CDM path using scheme
        '''
        return self.cdmLocale.getURI(path, protocol)
    
    def _toPOFile(self, catalog):
        '''
        Convert the catalog to a PO file like object.
    
        @param catalog: Catalog
            The catalog to convert to a file.
        @return: file read object
            A file like object to read the PO file from.
        '''
        assert isinstance(catalog, Catalog), 'Invalid catalog %s' % catalog
    
        fileObj = BytesIO()
        write_po(fileObj, catalog, **self.write_po_config)
        fileObj.seek(0)
        return fileObj
    