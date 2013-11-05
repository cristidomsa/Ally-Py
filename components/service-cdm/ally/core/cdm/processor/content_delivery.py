'''
Created on Jul 14, 2011

@package: service CDM
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mugur Rus

Provides the content delivery handler.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.http.spec.codes import METHOD_NOT_AVAILABLE, PATH_NOT_FOUND, \
    PATH_FOUND, CodedHTTP
from ally.http.spec.server import HTTP_GET
from ally.support.util_io import IInputStream
from mimetypes import guess_type
from os.path import isdir, isfile, join, normpath
from urllib.parse import unquote
import logging
import os

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    scheme = requires(str)
    uri = requires(str)
    method = requires(str)

class Response(CodedHTTP):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    allows = defines(set, doc='''
    @rtype: set(string)
    Contains the allow set for the methods.
    ''')

class ResponseContent(Context):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    source = defines(IInputStream, doc='''
    @rtype: IInputStream
    The stream that provides the response content in bytes.
    ''')
    length = defines(int, doc='''
    @rtype: integer
    Contains the length for the content.
    ''')
    type = defines(str, doc='''
    @rtype: string
    The type for the streamed content.
    ''')
    charSet = defines(str, doc='''
    @rtype: string
    The char set encoding for streamed content.
    ''')

# --------------------------------------------------------------------

@injected
class ContentDeliveryHandler(HandlerProcessor):
    '''
    Implementation for a processor that delivers the content based on the URL.
    '''

    repositoryPaths = list
    # The directory where the file repository is
    defaultContentType = 'application/octet-stream'
    # The default mime type to set on the content response if None could be guessed

    def __init__(self):
        assert isinstance(self.repositoryPaths, list), 'Invalid repository paths value %s' % self.repositoryPaths
        assert isinstance(self.defaultContentType, str), 'Invalid default content type %s' % self.defaultContentType
        self.repositoryPaths = [ normpath(path) for path in self.repositoryPaths ]
        if __debug__:
            for path in self.repositoryPaths:
                assert isinstance(path, str), 'Invalid repository path value %s' % path
                if not isdir(path):
                    log.warning('Directory %s does not exist', path)
                    if not os.access(path, os.R_OK):
                        log.warning('Unable to access the repository directory %s', path)
        super().__init__()

    def process(self, chain, request:Request, response:Response, responseCnt:ResponseContent, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provide the file content as a response.
        '''
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response
        assert isinstance(responseCnt, ResponseContent), 'Invalid response content %s' % responseCnt

        if request.method != HTTP_GET:
            if response.allows is not None: response.allows.add(HTTP_GET)
            else: response.allows = set((HTTP_GET,))
            METHOD_NOT_AVAILABLE.set(response)
            return

        # Initialize the read file handler with None value
        # This will be set upon successful file open
        rf, size = None, None
        for repositoryPath in self.repositoryPaths:
            entryPath = normpath(join(repositoryPath, unquote(request.uri)))
            # Make sure the given path points inside the repository
            if not entryPath.startswith(repositoryPath):
                break
            elif isfile(entryPath):
                rf, size = open(entryPath, 'rb'), os.path.getsize(entryPath)
    
        if rf is None:
            PATH_NOT_FOUND.set(response)
        else:
            PATH_FOUND.set(response)
            responseCnt.source = rf
            responseCnt.length = size
            responseCnt.type, responseCnt.charSet = guess_type(entryPath)
            if not responseCnt.type: responseCnt.type = self.defaultContentType
            return
