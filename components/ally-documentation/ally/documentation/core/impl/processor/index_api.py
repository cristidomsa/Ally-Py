'''
Created on Oct 8, 2013

@package: ally documentation
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that provides the API data to be documented.
'''

from ally.api.operator.type import TypeModel, TypeCall, TypeService, \
    TypeProperty
from ally.api.type import Type, Iter
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.http.spec.server import HTTP_PUT, HTTP_LINK, HTTP_GET


# --------------------------------------------------------------------
class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    invokers = requires(list)

class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    path = requires(list)
    methodHTTP = requires(str)
    output = requires(Type)
    target = requires(TypeModel)
    isCollection = requires(bool)
    call = requires(TypeCall)
    
class Element(Context):
    '''
    The element context.
    '''
    # ---------------------------------------------------------------- Required
    name = requires(str)
    
class Document(Context):
    '''
    The introspect context.
    '''
    # ---------------------------------------------------------------- Defined
    data = defines(dict, doc='''
    @rtype: dictionary{string: object}
    The data constructed for templates.
    ''')
    invokerData = defines(list, doc='''
    @rtype: list[tuple(Context, dictionary{string: object})]
    The list containing tuples with the invoker context and the data dictionary associated with it.
    ''')
      
# --------------------------------------------------------------------

class IndexAPIHandler(HandlerProcessor):
    '''
    Handler that provides the API data to be documented.
    '''
    
    def __init__(self):
        super().__init__(Invoker=Invoker, Element=Element)
    
    def process(self, chain, register:Register, document:Document, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Index the API data to be documented.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        assert isinstance(document, Document), 'Invalid document %s' % document
        if not register.invokers: return  # No invokers to process.

        if document.data is None: document.data = {}
        if document.invokerData is None: document.invokerData = []
        
        requests = document.data.get('requests')
        if requests is None: requests = document.data['requests'] = []
        
        methods = document.data.get('methods')
        if methods is None: methods = document.data['methods'] = {}

        for invoker in register.invokers:
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            if not invoker.path: continue
            
            request = {}
            requests.append(request)
            
            method = invoker.methodHTTP
            if method == HTTP_PUT and invoker.target is None: method = HTTP_LINK
            
            mrequests = methods.get(method)
            if mrequests is None: mrequests = methods[method] = []
            mrequests.append(request)
            
            request['path'] = '/'.join(el.name if el.name else '*' for el in invoker.path)
            request['method'] = method
            assert isinstance(invoker.call, TypeCall), 'Invalid invoker call %s' % invoker.call
            assert isinstance(invoker.call.parent, TypeService), 'Invalid call parent %s' % invoker.call.parent
            request['call'] = '%s.%s.%s' % (invoker.call.parent.clazz.__module__,
                                            invoker.call.parent.clazz.__name__, invoker.call.name)
            
            if invoker.target:
                assert isinstance(invoker.target, TypeModel), 'Invalid target %s' % invoker.target
                request['target'] = '%s.%s' % (invoker.target.clazz.__module__, invoker.target.clazz.__name__)
            
            flags = request['flags'] = set()
            
            if method == HTTP_GET:
                assert isinstance(invoker.target, TypeModel), 'Invalid target %s' % invoker.target
                if invoker.isCollection:
                    flags.add('isCollection')
                    assert isinstance(invoker.output, Iter), 'Invalid output %s' % invoker.output
                    output = invoker.output.itemType
                else: output = invoker.output
                
                if output == invoker.target: flags.add('isModel')
                elif output == invoker.target.propertyId: flags.add('isModelRef')
                else:
                    assert isinstance(output, TypeProperty), 'Invalid type property %s' % output
                    request['property'] = output.name
            
            document.invokerData.append((invoker, request))
        
        requests.sort(key=lambda request: request['path'])
        requests.sort(key=lambda request: request['method'])
        
        for mrequests in methods.values():
            mrequests.sort(key=lambda request: request['path'])
