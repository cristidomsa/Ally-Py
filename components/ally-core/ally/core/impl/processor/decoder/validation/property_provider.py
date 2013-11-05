'''
Created on Oct 29, 2013

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the properties validation.
'''

import logging

from ally.api.operator.type import TypeProperty, TypeService
from ally.api.validate import IValidation
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor
from ally.support.util_sys import locationStack, isLocated


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    validations = requires(dict)
    
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    service = requires(TypeService)
    
class Decoding(Context):
    '''
    The model decoding context.
    '''
    # ---------------------------------------------------------------- Defined
    validations = defines(list, doc='''
    @rtype: list[Validation]
    The list of validations to process for the property, this list needs to be consumed
    of the validations that are resolved.
    ''')
    # ---------------------------------------------------------------- Required
    property = requires(TypeProperty)

# --------------------------------------------------------------------

class ValidationPropertyProvider(HandlerProcessor):
    '''
    Implementation for a handler that provides the properties validation requirements.
    '''
    
    def process(self, chain, register:Register, invoker:Invoker, decoding:Decoding, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provide the validations for the property.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(register, Register), 'Invalid register %s' % register
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        assert isinstance(decoding, Decoding), 'Invalid decoding %s' % decoding
        
        if not register.validations: return
        if not decoding.property: return
        assert isinstance(decoding.property, TypeProperty), 'Invalid property type %s' % decoding.property
        
        svalidations = register.validations.get(invoker.service)
        if not svalidations: return
        assert isinstance(svalidations, list), 'Invalid validations %s' % svalidations
        
        k, validations = 0, []
        while k < len(svalidations):
            validation, target = svalidations[k]
            k += 1
            if not isinstance(validation, IValidation):
                if isLocated(target): log.warn('Cannot use validation %s from:%s', validation, locationStack(target))
                else: log.warn('Cannot use validation %s from target %s', validation, target)
                k -= 1
                del svalidations[k]
                continue
            
            assert isinstance(validation, IValidation)
            if validation.isFor(decoding.property): validations.append(validation)
        if not validations: return
        
        decoding.validations = validations
        chain.onFinalize(self.checkUnhandled)
    
    # ----------------------------------------------------------------

    def checkUnhandled(self, final, decoding, **keyargs):
        '''
        Checks if all validations have been handled.
        '''
        assert isinstance(decoding, Decoding), 'Invalid decoding %s' % decoding
        if decoding.validations: log.warn('Unknown validation specifications:\n\t%s',
                                          '\t\n'.join(str(valid) for valid in decoding.validations))
