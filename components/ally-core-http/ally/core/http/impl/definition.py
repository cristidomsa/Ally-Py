'''
Created on Jul 12, 2013

@package: ally core
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides verifiers for definitions.
'''

from ally.core.impl.definition import VerifierOperator, InputType
from ally.core.spec.definition import IValue
from ally.design.processor.attribute import requires, optional
from ally.design.processor.context import Context
from ally.design.processor.resolvers import merge
from ally.support.util import Singletone


# --------------------------------------------------------------------
class Relation(Singletone, VerifierOperator, IValue):
    '''
    Implementation for a @see: IVerifier, IValue that validates and fetches the relation of a decoding.
    '''

    class Decoding(Context):
        '''
        The decoding context.
        '''
        # ---------------------------------------------------------------- Optional
        relation = optional(Context)
        
    class Invoker(Context):
        '''
        The invokers context.
        '''
        # ---------------------------------------------------------------- Required
        path = requires(list)
        
    class Element(Context):
        '''
        The element context.
        '''
        # ---------------------------------------------------------------- Required
        name = requires(str)

    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Definition=InputType.Definition,
                              Decoding=Relation.Decoding, Invoker=Relation.Invoker, Element=Relation.Element))

    def isValid(self, definition):
        '''
        @see: IVerifier.isValid
        '''
        assert isinstance(definition, InputType.Definition), 'Invalid definition %s' % definition
        if not definition.decoding: return False
        if Relation.Decoding.relation not in definition.decoding: return False
        if definition.decoding.relation is None: return False
        return True
    
    def get(self, definition):
        '''
        @see: IValue.get
        '''
        assert isinstance(definition, InputType.Definition), 'Invalid definition %s' % definition
        if not definition.decoding: return
        if Relation.Decoding.relation not in definition.decoding or definition.decoding.relation is None: return
        assert isinstance(definition.decoding.relation, Relation.Invoker), \
        'Invalid relation %s' % definition.decoding.relation
        if not definition.decoding.relation.path: return
        
        path = []
        for el in definition.decoding.relation.path:
            assert isinstance(el, Relation.Element), 'Invalid element %s' % el
            if el.name: path.append(el.name)
            else: path.append('*')
        
        return '/'.join(path)
