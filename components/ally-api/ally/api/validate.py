'''
Created on Oct 29, 2013

@package: ally api
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the validation marking mechanism, this module contains classes that allow for model marking.
'''

from ally.api.operator.type import TypeProperty, TypeModel, \
    TypePropertyContainer
from ally.api.type import typeFor
import abc
from ally.support.api.util_service import isCompatible


# --------------------------------------------------------------------

class IValidation(metaclass=abc.ABCMeta):
    '''
    The validation specification.
    '''
    
    @abc.abstractmethod
    def isFor(self, target):
        '''
        Checks if the validation is for the provided target.
        
        @param target: object
            The target to check.
        @return: boolean
            True if the validation is for the provided target, False otherwise.
        '''
    
class ValidationProperty(IValidation):
    '''
    The validation basic property target container class.
    '''
    
    def __init__(self, prop):
        '''
        Create the validation.
        
        @param prop: TypeProperty reference
            The property to register the validation to.
        '''
        ptype = typeFor(prop)
        assert isinstance(ptype, TypeProperty), 'Invalid property %s' % prop
        assert isinstance(ptype.parent, TypeModel), 'Invalid property model %s' % ptype.parent
        
        self.property = ptype
        
    def isFor(self, target):
        '''
        @see: IValidation.isFor
        '''
        return isCompatible(self.property, target)
        
    def __str__(self):
        return '%s:%s' % (self.property, self.__class__.__name__)
        
# --------------------------------------------------------------------

class Mandatory(ValidationProperty):
    '''
    Mandatory property type validation.
    '''
    
    def __init__(self, prop):
        '''
        @see: Validation
        '''
        super().__init__(prop)
        
class ReadOnly(ValidationProperty):
    '''
    Read only property type validation.
    '''
    
    def __init__(self, prop):
        '''
        @see: Validation
        '''
        super().__init__(prop)

class AutoId(ValidationProperty):
    '''
    Auto generated id property type validation.
    '''
    
    def __init__(self, prop):
        '''
        @see: Validation
        '''
        super().__init__(prop)

class MaxLen(ValidationProperty):
    '''
    String property maximum length type validation.
    '''
    
    def __init__(self, prop, length):
        '''
        @see: Validation
        
        @param length: integer
            The maximum length.
        '''
        assert isinstance(length, int), 'Invalid length %s' % length
        super().__init__(prop)
        
        self.length = length

class Relation(ValidationProperty):
    '''
    Relation property type with other models validation.
    '''
    
    def __init__(self, prop):
        '''
        @see: Validation
        '''
        assert isinstance(prop, TypePropertyContainer), 'Invalid property type %s' % prop
        super().__init__(prop)

# --------------------------------------------------------------------

def validate(validation, *validations):
    '''
    Decorator used for binding validations or validation targets on support objects.
    The purpose of this is just to say that for a certain class, attribute or even object there are some validations
    that are required.
    Even though the validations are binded there needs to be other mechanism that manages the validations, so even
    if the validation can be binded anyware it doesn't mean necessarily that is used.
    
    @param validation: object
        The validation or validation target to be binded by the decorator.
    @param validations: argument[object]
        Additional validations to be binded.
    '''
    assert validation is not None, 'None is not a validation'
    if __debug__:
        for valid in validations: assert valid is not None, 'None is not a validation'
    def decorator(target):
        try: current = target._ally_validations
        except AttributeError: current = target._ally_validations = []
        current.append(validation)
        current.extend(validations)
        return target
    return decorator

def validationsFor(obj):
    '''
    Provides the validations binded to the provided object.
    @see: validate
    
    @param obj: object
        The object to extract the validations from.
    @return: list[object, target]
        A list that provides on the first position the binded validation target and on the second
        the binded target
    '''
    assert obj is not None, 'None is not a validation target'
    
    validations = []
    try:
        for validation in obj._ally_validations:  validations.append((validation, obj))
    except AttributeError: pass
    return validations
