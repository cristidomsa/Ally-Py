'''
Created on Oct 9, 2013

@package: ally documentation
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Processor that provides register definition descriptions indexing.
'''

from collections import OrderedDict

from ally.container.ioc import injected
from ally.core.spec.definition import IVerifier
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor

from ..definition import resolversForDescriptions, indexDefinition


# --------------------------------------------------------------------
class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    definitions = requires(list)
    
class Document(Context):
    '''
    The introspect context.
    '''
    # ---------------------------------------------------------------- Defined
    data = defines(dict, doc='''
    @rtype: dictionary{string: object}
    The data constructed for templates.
    ''')
      
# --------------------------------------------------------------------

@injected
class DefinitionRegisterHandler(HandlerProcessor):
    '''
    Handler that provides the definition indexing for register definitions.
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
        super().__init__(**resolvers)
    
    def process(self, chain, register:Register, document:Document, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Index the regiter definition data to be documented.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        assert isinstance(document, Document), 'Invalid document %s' % document
        if not register.definitions: return  # No definitions to process.

        if document.data is None: document.data = {}
        data = document.data.get(self.name)
        if data is None: data = document.data[self.name] = OrderedDict()
        
        for defin in register.definitions:
            if not self.verifier.isValid(defin): continue
            indexDefinition(defin, data, self.descriptions)
            
