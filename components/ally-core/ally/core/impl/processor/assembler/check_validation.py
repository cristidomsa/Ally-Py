'''
Created on Nov 1, 2013

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Checks if there are validations on the persist targets.
'''

import logging

from ally.api.config import UPDATE, INSERT
from ally.api.operator.type import TypeService, TypeModel
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    invokers = requires(list)
    validations = requires(dict)
    
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    service = requires(TypeService)
    method = requires(int)
    target = requires(TypeModel)
    location = requires(str)
    
# --------------------------------------------------------------------

class CheckValidationHandler(HandlerProcessor):
    '''
    Implementation for a processor that checks if there are validations on the persist targets.
    '''
    
    def __init__(self):
        super().__init__(Invoker=Invoker)

    def process(self, chain, register:Register, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Check if there are validations.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        if not register.invokers: return  # No invokers to process.
        if not register.validations: return
        
        for invoker in register.invokers:
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            if invoker.method not in (INSERT, UPDATE): continue
            if not invoker.target: continue
            
            svalidations = register.validations.get(invoker.service)
            if not svalidations:
                log.warn('No validations have been registered for \'%s\', persisted at:%s',
                         invoker.target, invoker.location)
