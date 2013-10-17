'''
Created on Oct 10, 2013

@package: ally documentation
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides support for definition indexing.
'''

from collections import deque

from ally.core.spec.definition import IVerifier, IValue
from ally.design.processor.attribute import optional, requires
from ally.design.processor.context import Context
from ally.design.processor.resolvers import resolversFor


# --------------------------------------------------------------------
class Definition(Context):
    '''
    The definition context.
    '''
    # ---------------------------------------------------------------- Optional
    isMandatory = optional(bool)
    enumeration = optional(list)
    references = optional(list)
    # ---------------------------------------------------------------- Required
    name = requires(str)
    types = requires(list)
    
# --------------------------------------------------------------------

def resolversForDescriptions(descriptions):
    '''
    Creates the resolvers for the provided descriptions verifiers.
    
    :param descriptions: The descriptions to use on the definition in order to index the description for definition.
    :type descriptions: list[tuple(IVerifier, tuple(string), dictionary{string: object})]
    :returns: dictionary{string: IResolver} -- The resolved dictionary.
    '''
    assert isinstance(descriptions, list), 'Invalid descriptions %s' % descriptions
    resolvers = resolversFor(dict(Definition=Definition))
    
    for verifier, descriptions, data in descriptions:
        assert isinstance(verifier, IVerifier), 'Invalid verifier %s' % verifier
        assert isinstance(descriptions, tuple), 'Invalid descriptions %s' % descriptions
        assert isinstance(data, dict), 'Invalid data %s' % data
        if __debug__:
            for desc in descriptions: assert isinstance(desc, str), 'Invalid description %s' % desc
        
        verifier.prepare(resolvers)
            
        for value in data.values():
            if isinstance(value, IValue):
                assert isinstance(value, IValue)
                value.prepare(resolvers)
                
    return resolvers
   
# --------------------------------------------------------------------

def indexDefinition(defin, data, descriptions):
    '''Index the definition in the provided data.
    
    :param defin: The definition context to index.
    :param data: The data where to index the definition.
    :type data: dictionary{string: object}
    :param descriptions: The descriptions to use on the definition in order to index the description for definition.
    :type descriptions: list[tuple(IVerifier, tuple(string), dictionary{string: object})]
    '''
    assert isinstance(defin, Definition), 'Invalid definition %s' % defin
    assert isinstance(data, dict), 'Invalid data %s' % data
    
    stack = deque()
    stack.append(defin)
    while stack:
        defin = stack.popleft()
        assert isinstance(defin, Definition), 'Invalid definition %s' % defin
        
        if Definition.references in defin and defin.references:
            stack.extendleft(defin.references)
        
        if defin.name and defin.name not in data:
            
            ddata = data[defin.name] = {}
            if Definition.enumeration in defin and defin.enumeration:
                ddata['enumeration'] = defin.enumeration
            elif defin.types: ddata['types'] = defin.types
            
            if Definition.isMandatory in defin and defin.isMandatory is not None:
                isMandatory = defin.isMandatory
            else: isMandatory = False
            ddata['isMandatory'] = isMandatory
            ddata['description'] = descriptionFor(defin, descriptions)
            
def descriptionFor(defin, descriptions):
    '''Construct the description for the provided definition.
    
    :param defin: The definition context to index.
    :param descriptions: The descriptions to use on the definition in order to index the description for definition.
    :returns: list[tuple(string, dictionary{string: object})] -- The list containing the description data.
    '''
    assert isinstance(defin, Definition), 'Invalid definition %s' % defin
    assert isinstance(descriptions, list), 'Invalid descriptions %s' % descriptions
    
    entries = []
    for verifier, descriptions, data in descriptions:
        assert isinstance(verifier, IVerifier), 'Invalid verifier %s' % verifier
        if verifier.isValid(defin):
            data = transformData(defin, data)
            for description in descriptions: entries.append((description, data))
    
    return entries

def transformData(defin, data):
    '''
    Transforms the data dictionary to proper values.
    
    :param defin: The definition context to index.
    :param data: The data where to index the definition.
    :type data: dictionary{string: object}
    :returns: dictionary{string: object} --  The transformed data.
    '''
    assert isinstance(data, dict), 'Invalid data %s' % data
    
    tansformed = {}
    for key, value in data.items():
        if isinstance(value, IValue):
            assert isinstance(value, IValue)
            value = value.get(defin)
        tansformed[key] = value
        
    return tansformed
