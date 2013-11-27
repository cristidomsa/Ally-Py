'''
Created on Nov 14, 2013
 
@package: internationlization
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Catalog manager implementation.
'''
import logging
import codecs
import abc
from babel.messages import catalog
from ally.container import wire
from babel.messages.catalog import Catalog
from ally.core.error import DevelError
from babel.messages.pofile import read_po, write_po
from babel.compat import BytesIO
from internationalization.core.spec import ICatalogManager
from ..service import globalMessagesName

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class CatalogManager(ICatalogManager):
    '''
    The PO file manager: processes and returns the global or plugin
    PO/POT files content from anywhere.
    '''

    default_charset = 'UTF-8'; wire.config('default_charset', doc='''
    The default character set to use whenever a PO file is uploaded and the character
    set of the content is not specified''')
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
    
    def __init__(self):
        assert isinstance(self.default_charset, str), 'Invalid default charset %s' % self.default_charset
        assert isinstance(self.write_po_config, dict), 'Invalid write PO configurations %s' % self.write_po_config
        
    def getGlobalPOCatalog(self, locale):
        '''
        @see: IPOFileManager.getGlobalPOCatalog
        '''
        name = globalMessagesName()
        content = self.getData(name=name, locale=locale)
        catalog = self._getCatalog(content, self.default_charset)
        if catalog:
            template = self.getGlobalPOTCatalog()
            if template: catalog.update(template)
            else: assert log.debug('Global POT file could not be generated. Check if you have any POTs in db') or True
        return catalog or None

    def getPluginPOCatalog(self, name, locale):
        '''
        @see: IPOFileManager.getPluginPOCatalog
        '''
        content = self.getData(name=name, locale=locale)
        catalog = self._getCatalog(content, self.default_charset)
        if catalog:
            template = self._getCatalog(self.getData(name=name), self.default_charset)
            if template: 
                catalog.update(template)
            else: assert log.debug('No POT file found for plugin {name}. Delivering not updated PO'.format(name=name)) or True
        return catalog or None

    def getGlobalPOTCatalog(self):
        '''
        @see: IPOFileManager.getGlobalPOTCatalog
        '''
        pots = self.getAllPOTs()
        template = Catalog()
        for name, in pots:
            template.update(self._getCatalog(self.getData(name), self.default_charset))
        return template or None
    
    def getPluginPOTCatalog(self, name):
        '''
        @see: IPOFileManager.getPluginPOTCatalog
        '''
        content = self.getData(name)
        catalog = self._getCatalog(content, self.default_charset)
        return catalog or None
    
    def updateGlobalPO(self, locale, poFile):
        '''
        @see IPOFileManager.updateGlobalPO
        '''
        name = globalMessagesName()
        encoding = poFile.charSet or self.default_charset
        poFile = codecs.getreader(encoding)(poFile)
        newCatalog = self._getCatalog(poFile, encoding)
        if not newCatalog: raise DevelError('Invalid po file provided. Please check')
        oldCatalog = self._getCatalog(self.getData(name=name, locale=locale))
        if oldCatalog:
            catalog = newCatalog.update(oldCatalog)
        else:
            catalog = newCatalog
        content = self._toFile(catalog)
        return self.storeData(name=name, locale=locale, content=content.getvalue())
    
    def updatePluginPO(self, name, locale, poFile):
        '''
        @see IPOFileManager.updatePluginPO
        '''
        encoding = poFile.charSet or self.default_charset
        try: poFile = codecs.getreader(encoding)(poFile)
        except UnicodeDecodeError: raise DevelError('Improper PO file')
        newCatalog = self._getCatalog(poFile, encoding)
        if not newCatalog: raise DevelError('Invalid po file provided. Please check')
        oldCatalog = self.getPluginPOCatalog(name=name, locale=locale)
        if oldCatalog:
            catalog = newCatalog.update(oldCatalog)
        else:
            catalog = newCatalog
        content = self._toFile(catalog)
        return self.storeData(name=name, locale=locale, content=content.getvalue())

    def updatePluginPOT(self, name, poFile):
        '''
        @see IPOFileManager.updatePluginPOT
        '''
        encoding = poFile.charSet or self.default_charset
        try: poFile = codecs.getreader(encoding)(poFile)
        except UnicodeDecodeError: raise DevelError('Invalid template provided') 
        newTemplate = self._getCatalog(poFile, encoding)
        content = self._toFile(newTemplate)
        return self.storeData(name=name, content=content.getvalue())
            
    # --------------------------------------------------------------------
    @abc.abstractmethod
    def getLatestTimestampForPO(self, name, locale):
        '''
        Provides latest timestamp for PO file
        '''
        
    @abc.abstractmethod
    def getLatestTimestampForPOT(self, name):
        '''
        Provides latest timestamp for POT file
        '''
    
    # --------------------------------------------------------------------
    
    def _getCatalog(self, content, encoding):
        '''
        Validate content and return PO messages catalog from it.
        '''
        try:
            return read_po(content)
        except:
            assert log.debug('Error reading po file', exc_info=1) or True
            try:
                return read_po(BytesIO(content))
            except:
                assert log.debug('content not a PO file!', exc_info=1) or True
                return
    
    def _toFile(self, catalog):
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