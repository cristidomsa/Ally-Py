'''
Created on Oct 30, 2013

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the maximum length validation.
'''

from ally.api.error import InputError
from ally.api.operator.type import TypeProperty
from ally.api.validate import MaxLen
from ally.design.processor.attribute import requires, definesIf
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.support.util_spec import IDo
from ally.internationalization import _


# --------------------------------------------------------------------
class Decoding(Context):
    '''
    The model decoding context.
    '''
    # ---------------------------------------------------------------- Defined
    maximumLength = definesIf(int, doc='''
    @rtype: integer
    Flag indicating if the decoding is mandatory.
    ''')
    # ---------------------------------------------------------------- Required
    validations = requires(list)
    property = requires(TypeProperty)
    doSet = requires(IDo)
    
# --------------------------------------------------------------------

class ValidateMaxLen(HandlerProcessor):
    '''
    Implementation for a handler that provides the maximum length validation.
    '''
    
    def process(self, chain, decoding:Decoding, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Process the maximum length validation.
        '''
        assert isinstance(decoding, Decoding), 'Invalid decoding %s' % decoding
        if not decoding.validations: return
        
        length, validations = None, []
        for validation in decoding.validations:
            if isinstance(validation, MaxLen):
                assert isinstance(validation, MaxLen)
                if length is None: length = validation.length
                else: length = min(length, validation.length)
            else: validations.append(validation)
        
        decoding.validations = validations

        if length is not None:
            if Decoding.maximumLength in decoding:
                decoding.maximumLength = length
            decoding.doSet = self.createSet(decoding.doSet, decoding.property, length)

    # ----------------------------------------------------------------
    
    def createSet(self, wrapped, prop, length):
        '''
        Create the do set to use with validation.
        '''
        assert callable(wrapped), 'Invalid wrapped set %s' % wrapped
        assert isinstance(prop, TypeProperty), 'Invalid property %s' % prop
        def doSet(target, value):
            if len(value) > length: raise InputError(_('Maximum allowed text size exceed'), prop)
            wrapped(target, value)
        return doSet
