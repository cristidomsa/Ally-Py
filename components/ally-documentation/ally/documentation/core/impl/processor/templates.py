'''
Created on Oct 8, 2013

@package: ally documentation
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that provides the Jinja2 templates for documentation.
'''

import os
from pkg_resources import get_provider, ResourceManager
import re

from jinja2.loaders import BaseLoader, DictLoader

from ally.container.ioc import injected
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.support.util_io import pipe, IClosable


# --------------------------------------------------------------------
class Document(Context):
    '''
    The document context.
    '''
    # ---------------------------------------------------------------- Defined
    loader = defines(BaseLoader, doc='''
    @rtype: BaseLoader
    The jinja loader for templates.
    ''')
      
# --------------------------------------------------------------------

@injected
class TemplateHandler(HandlerProcessor):
    '''
    Handler that provides the Jinja2 templates for documentation.
    '''
    
    pathDocumentation = str
    # The folder where the documentation will be placed.
    packageName = str
    # The package name where the templates are located.
    pathsTemplates = list
    # The paths where additional templates can be found. 
    patternTemplate = str
    # The pattern used for identify the template paths.
    patternCopy = str
    # The pattern used for identify the resource paths to copied.
    
    packagePath = 'templates'
    # The package templates folder path.
    
    def __init__(self):
        assert isinstance(self.pathDocumentation, str), 'Invalid documentation path %s' % self.pathDocumentation
        assert isinstance(self.packageName, str), 'Invalid package name %s' % self.packageName
        assert isinstance(self.pathsTemplates, list), 'Invalid templates paths %s' % self.pathsTemplates
        assert isinstance(self.patternTemplate, str), 'Invalid template pattern %s' % self.patternTemplate
        assert isinstance(self.patternCopy, str), 'Invalid template copy %s' % self.patternCopy
        assert isinstance(self.packagePath, str), 'Invalid package path %s' % self.packagePath
        super().__init__()
        
        self._packageProvider = get_provider(self.packageName)
        self._manager = ResourceManager()
        
        self._rPatternTemplate = re.compile(self.patternTemplate)
        self._rPatternCopy = re.compile(self.patternCopy)
    
    def process(self, chain, document:Document, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Process the jinja templates.
        '''
        assert isinstance(document, Document), 'Invalid document %s' % document
        
        templates = {}
        for path, stream in self.listPaths().items():
            if self._rPatternTemplate.match(path):
                try: templates[path] = stream.read().decode('utf8')
                finally:
                    if isinstance(stream, IClosable): stream.close()
            elif self._rPatternCopy.match(path):
                try: folder = path[:path.index('/')]
                except ValueError: folder = self.pathDocumentation
                else: folder = os.path.join(self.pathDocumentation, folder.replace('/', os.sep))
                
                if not os.path.exists(folder): os.makedirs(folder)
                file = os.path.join(self.pathDocumentation, path.replace('/', os.sep))
                
                try:
                    with open(file, 'wb') as dest: pipe(stream, dest)
                finally:
                    if isinstance(stream, IClosable): stream.close()
        
        document.loader = DictLoader(templates)
        
    def listPaths(self):
        '''
        Lists the template folder paths.
        '''
        results = {}
        
        path = self.packagePath
        if path[:2] == './':
            path = path[2:]
        elif path == '.':
            path = ''
        offset = len(path)
        
        def walk(path):
            for fileName in self._packageProvider.resource_listdir(path):
                fullPath = path + '/' + fileName
                if self._packageProvider.resource_isdir(fullPath): walk(fullPath)
                else:
                    stream = self._packageProvider.get_resource_stream(self._manager, fullPath)
                    results[fullPath[offset:].lstrip('/')] = stream
        walk(path)
        
        for path in self.pathsTemplates:
            for dirPath, _dirNames, fileNames in os.walk(path):
                for fileName in fileNames:
                    fullPath = os.path.join(dirPath, fileName)
                    template = fullPath[len(path):].strip(os.path.sep).replace(os.path.sep, '/')
                    if template[:2] == './': template = template[2:]
                    results[template] = open(fullPath, 'rb')
        
        return results
