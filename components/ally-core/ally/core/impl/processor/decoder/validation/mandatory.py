'''
Created on Oct 29, 2013

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the mandatory validation.
'''

from ally.api.config import INSERT
from ally.api.validate import Mandatory
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
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
    # ---------------------------------------------------------------- Defined
    isMandatory = defines(bool, doc='''
    @rtype: boolean
    Flag indicating if the decoding is mandatory.
    ''')
    # ---------------------------------------------------------------- Required
    validations = requires(list)
    
# --------------------------------------------------------------------

class ValidateMandatory(HandlerProcessor):
    '''
    Implementation for a handler that provides the mandatory validation.
    '''
    
    def process(self, chain, decoding:Decoding, invoker:Invoker, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Process the mandatory validation.
        '''
        assert isinstance(decoding, Decoding), 'Invalid decoding %s' % decoding
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        if not decoding.validations: return
        
        found, validations = False, []
        for validation in decoding.validations:
            if isinstance(validation, Mandatory):
                found = True
            else: validations.append(validation)
        if not found: return
        
        if invoker.method == INSERT: decoding.isMandatory = True
        
        decoding.validations = validations
