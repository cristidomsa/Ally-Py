'''
Created on Nov 1, 2013

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the SQL Alchemy validation based on meta mappings.
'''

from inspect import isclass
import logging
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.schema import MetaData
from sqlalchemy.types import String

from ally.api.operator.type import TypeModel, TypePropertyContainer
from ally.api.type import typeFor
from ally.api.validate import IValidation, AutoId, Mandatory, MaxLen, Relation, \
    validationsFor
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.support.util_sys import getAttrAndClass
from sql_alchemy.support.mapper import DeclarativeMetaModel, mappingFor


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    validations = requires(dict)
    
# --------------------------------------------------------------------

class MappedValidationHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the SQL Alchemy validation based on meta mappings.
    '''

    def process(self, chain, register:Register, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Register the vlaidations based on the meta data definitions.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        if not register.validations: return
        
        for validations in register.validations.values():
            assert isinstance(validations, list), 'Invalid validations %s' % validations
            
            k, mvalidations = 0, []
            while k < len(validations):
                validation, _target = validations[k]
                k += 1
                if isinstance(validation, DeclarativeMetaModel):
                    mvalidations.extend(self.validations(validation))
                    k -= 1
                    del validations[k]
                    continue
            validations.extend(mvalidations)

    def validations(self, mapped):
        '''
        Provides the mapped class validations that can be performed based on the SQL alchemy mapping.
        
        @param mapped: class
            The mapped model class.
        @return: list[Validation, DeclarativeMetaModel]
            The list of validations obtained.
        '''
        assert isclass(mapped), 'Invalid class %s' % mapped
        assert isinstance(mapped.metadata, MetaData), 'Invalid mapped class %s' % mapped
        mapper, model = mappingFor(mapped), typeFor(mapped)
        assert isinstance(mapper, Mapper), 'Invalid mapped class %s' % mapped
        assert isinstance(model, TypeModel), 'Invalid model class %s' % mapped

        validations = []
        mvalidations = validationsFor(mapped)
        if mvalidations:
            for validation, target in mvalidations:
                assert isinstance(validation, IValidation), 'Invalid created validation %s' % validation
                validations.append((validation, target))
        
        for name, prop in model.properties.items():
            descriptor, dclazz = getAttrAndClass(mapped, name)
            dvalidations = validationsFor(descriptor)
            if dvalidations:
                for creator, target in dvalidations:
                    validation = creator(prop)
                    assert isinstance(validation, IValidation), 'Invalid created validation %s' % validation
                    if target == descriptor: target = dclazz
                    validations.append((validation, target))
                continue
            
            column = getattr(mapper.c, name, None)
            if column is None: continue
    
            if column.primary_key:
                if column.autoincrement: validations.append((AutoId(prop), mapped))
                else: validations.append((Mandatory(prop), mapped))
            elif not column.nullable: validations.append((Mandatory(prop), mapped))
    
            if isinstance(column.type, String) and column.type.length:
                validations.append((MaxLen(prop, column.type.length), mapped))
            
            if isinstance(prop, TypePropertyContainer): validations.append((Relation(prop), mapped))
            
        return validations        
