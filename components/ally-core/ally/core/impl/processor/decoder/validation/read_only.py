'''
Created on Oct 29, 2013

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the read only validation.
'''


from ally.api.config import INSERT
from ally.api.validate import ReadOnly
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor


# --------------------------------------------------------------------
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    method = requires(int)
    
class Decoding(Context):
    '''
    The model decoding context.
    '''
    # ---------------------------------------------------------------- Required
    validations = requires(list)
    
# --------------------------------------------------------------------

class ValidateReadOnly(HandlerProcessor):
    '''
    Implementation for a handler that provides the read only validation.
    '''
    
    def process(self, chain, decoding:Decoding, invoker:Invoker, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Process the read only validation.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(decoding, Decoding), 'Invalid decoding %s' % decoding
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not decoding.validations: return
        
        found, validations = False, []
        for validation in decoding.validations:
            if isinstance(validation, ReadOnly):
                found = True
            else: validations.append(validation)
        if not found: return
        
        if invoker.method == INSERT:
            validations = []  # This validation overrides all other.
            chain.cancel()  # For insert there is no need for property, is read only.
        
        decoding.validations = validations
