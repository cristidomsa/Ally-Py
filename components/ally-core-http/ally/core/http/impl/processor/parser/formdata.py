'''
Created on Aug 31, 2012

package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the multipart form-data conversion to url encoded content.
'''

from ally.container.ioc import injected
from ally.core.http.impl.processor.base import ErrorResponseHTTP
from ally.core.http.spec.codes import MUTLIPART_ERROR
from ally.core.impl.processor.base import addError
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.support.util_io import IInputStream
from ally.support.util_spec import IDo
from io import BytesIO
from urllib.parse import urlencode
import logging
import re

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class RequestContent(Context):
    '''
    The request content context.
    '''
    # ---------------------------------------------------------------- Defined
    name = defines(str, doc='''
    @rtype: string
    The content disposition file name.
    ''')
    # ---------------------------------------------------------------- Required
    type = requires(str)
    charSet = requires(str)
    disposition = requires(str)
    dispositionAttr = requires(dict)
    source = requires(IInputStream)
    previousContent = requires(Context)
    doFetchNextContent = requires(IDo)

# --------------------------------------------------------------------

@injected
class ParseFormDataHandler(HandlerProcessor):
    '''
    Provides the multi part form data content handler processor.
    '''

    regexMultipart = '^multipart/form\-data$'
    # The regex for the content type value that dictates that the content is multi part form data.

    charSet = 'ASCII'
    # The character set used in decoding the form data.
    contentTypeUrlEncoded = str
    # The content type to set on the URL encoded form data.
    contentDisposition = 'form-data'
    # The content disposition for the form data.
    attrContentDispositionName = 'name'
    # The content disposition name.
    attrContentDispositionFile = 'filename'
    # The content disposition name.

    def __init__(self):
        assert isinstance(self.regexMultipart, str), 'Invalid multi part regex %s' % self.regexMultipart
        assert isinstance(self.charSet, str), 'Invalid character set %s' % self.charSet
        assert isinstance(self.contentTypeUrlEncoded, str), \
        'Invalid content type URL encoded %s' % self.contentTypeUrlEncoded
        assert isinstance(self.contentDisposition, str), 'Invalid content disposition %s' % self.contentDisposition
        assert isinstance(self.attrContentDispositionName, str), \
        'Invalid content disposition name attribute %s' % self.attrContentDispositionName
        assert isinstance(self.attrContentDispositionFile, str), \
        'Invalid content disposition file attribute %s' % self.attrContentDispositionFile
        super().__init__()

        self._reMultipart = re.compile(self.regexMultipart)

    def process(self, chain, requestCnt:RequestContent, response:ErrorResponseHTTP, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Process the multi part data.
        '''
        assert isinstance(requestCnt, RequestContent), 'Invalid request content %s' % requestCnt
        assert isinstance(response, ErrorResponseHTTP), 'Invalid response %s' % response

        if requestCnt.previousContent is None: return
        # If there is no previous content it means that this is not a multi part request content.
        multiCnt = requestCnt.previousContent
        assert isinstance(multiCnt, RequestContent), 'Invalid request content %s' % multiCnt

        if not multiCnt.type or not self._reMultipart.match(multiCnt.type): return
        assert log.debug('Content type %s is multi part form data', multiCnt.type) or True

        content, parameters = requestCnt, []
        while True:
            if content.disposition != self.contentDisposition:
                MUTLIPART_ERROR.set(response)
                return addError(response, 'Invalid multipart form data content disposition \'%s\'' % content.disposition)

            name = content.dispositionAttr.pop(self.attrContentDispositionFile, None)
            if name is not None:
                content.name = name
                break

            name = content.dispositionAttr.pop(self.attrContentDispositionName, None)
            if not name:
                MUTLIPART_ERROR.set(response)
                return addError(response, 'Missing the content disposition header attribute name')

            parameters.append((name, str(content.source.read(), requestCnt.charSet)))

            content = content.doFetchNextContent()
            if not content: break
            assert isinstance(content, RequestContent), 'Invalid request content %s' % content

        if parameters:
            requestCnt.type = self.contentTypeUrlEncoded
            requestCnt.charSet = self.charSet
            requestCnt.doFetchNextContent = lambda: content
            requestCnt.source = BytesIO(urlencode(parameters).encode(self.charSet, 'replace'))
