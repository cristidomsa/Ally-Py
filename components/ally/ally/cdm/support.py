'''
Created on Apr 11, 2012

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provide support classes for the CDM handling.
'''

from .spec import ICDM

# --------------------------------------------------------------------

class ExtendPathCDM(ICDM):
    '''
    Provides a CDM that delegates the call to a wrapped CDM but before that it alters the path.
    @see: ICDM
    '''

    def __init__(self, wrapped, format):
        '''
        Construct the extend path CDM.
        
        @param wrapped: ICDM
            The wrapped CDM.
        @param format: string
            The format to apply to the path before being delivered to the wrapped CDM, something like 'my_root_folder/%s'
        '''
        assert isinstance(wrapped, ICDM), 'Invalid wrapped CDM %s' % wrapped
        assert isinstance(format, str), 'Invalid path format %s' % format
        self.wrapped = wrapped
        self.format = format

    def publishFromFile(self, path, filePath, metadata):
        '''
        @see: ICDM.publishFromFile
        '''
        self.wrapped.publishFromFile(self.format % path, filePath, metadata)

    def publishContent(self, path, content, metadata):
        '''
        @see: ICDM.publishContent
        '''
        self.wrapped.publishContent(self.format % path, content. metadata)
        
    def updateMetadata(self, path, metadata):
        '''
        @see: ICDM.publishMetadata
        '''
        self.wrapped.updateMetadata(self.format % path, metadata)

    def republish(self, oldPath, newPath):
        '''
         @see: ICDM.republish
        '''    
        self.wrapped.republish(self.format % oldPath, self.format % newPath)

    def remove(self, path):
        '''
        @see: ICDM.remove
        '''
        self.wrapped.remove(self.format % path)

    def getSupportedProtocols(self):
        '''
        @see: ICDM.getSupportedProtocols
        '''
        return self.wrapped.getSupportedProtocols()

    def getURI(self, path, protocol):
        '''
        @see: ICDM.getURI
        '''
        return self.wrapped.getURI(self.format % path, protocol)

    def getMetadata(self, path):
        '''
        @see ICDM.getMetadata
        '''
        return self.wrapped.getMetadata(self.format % path)
