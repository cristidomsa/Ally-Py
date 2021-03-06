'''
Created on Nov 23, 2011

@package: ally http
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides a processor that just sends an ok status as a response without any body. This is useful for the OPTIONS
method for instance where we just want to deliver some response headers. 
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor
from ally.http.spec.codes import PATH_FOUND, CodedHTTP

# --------------------------------------------------------------------

class Request(Context):
    '''
    The request context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(str)

class Response(CodedHTTP):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    allows = defines(set)

# --------------------------------------------------------------------

@injected
class DeliverOkForMethodHandler(HandlerProcessor):
    '''
    Handler that just sends an ok status.
    '''

    forMethod = str
    # The method to respond with Ok for.

    def __init__(self):
        assert isinstance(self.forMethod, str), 'Invalid for method %s' % self.forMethod
        super().__init__()

    def process(self, chain, request:Request, response:Response, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Delivers Ok if the request methos is the expected one.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain
        assert isinstance(request, Request), 'Invalid request %s' % request
        assert isinstance(response, Response), 'Invalid response %s' % response

        if request.method == self.forMethod:
            PATH_FOUND.set(response)
            chain.cancel()
            return

        if response.allows is None: response.allows = set()
        response.allows.add(self.forMethod)
