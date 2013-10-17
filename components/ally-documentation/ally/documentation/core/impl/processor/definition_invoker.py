'''
Created on Oct 10, 2013

@package: ally documentation
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that provides invoker definition descriptions indexing.
'''

from collections import OrderedDict

from ally.container.ioc import injected
from ally.core.spec.definition import IVerifier
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.design.processor.resolvers import solve

from ..definition import resolversForDescriptions, indexDefinition


# --------------------------------------------------------------------
class Document(Context):
    '''
    The introspect context.
    '''
    # ---------------------------------------------------------------- Required
    invokerData = requires(list)

class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    definitions = requires(list)
    
# --------------------------------------------------------------------

@injected
class DefinitionInvokerHandler(HandlerProcessor):
    '''
    Handler that provides the definition indexing for invoker definitions.
    '''
    
    name = str
    # The name to publish the definitions in data.
    verifier = IVerifier
    # The verifier used on the register definition in order to extract the headers.
    descriptions = list
    # The descriptions (list[tuple(IVerifier, tuple(string), dictionary{string: object})]) used in constructing the error.
    
    def __init__(self):
        assert isinstance(self.name, str), 'Invalid name %s' % self.name
        assert isinstance(self.verifier, IVerifier), 'Invalid verifier %s' % self.verifier
        assert isinstance(self.descriptions, list), 'Invalid descriptions %s' % self.descriptions
        
        resolvers = resolversForDescriptions(self.descriptions)
        self.verifier.prepare(resolvers)
        solve(resolvers, dict(Invoker=Invoker))
        
        super().__init__(**resolvers)
    
    def process(self, chain, document:Document, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Index the regiter definition data to be documented.
        '''
        assert isinstance(document, Document), 'Invalid document %s' % document
        if not document.invokerData: return  # No invoker data to process.

        for invoker, data in document.invokerData:
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            if not invoker.definitions: continue
            
            for defin in invoker.definitions:
                if not self.verifier.isValid(defin): continue
                ddata = data.get(self.name)
                if ddata is None: ddata = data[self.name] = OrderedDict()
                indexDefinition(defin, ddata, self.descriptions)
