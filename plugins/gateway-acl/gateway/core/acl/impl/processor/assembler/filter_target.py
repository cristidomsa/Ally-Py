'''
Created on Aug 12, 2013

@package: gateway acl
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the filters target.
'''

from ally.api.operator.type import TypeProperty
from ally.container.ioc import injected
from ally.container.support import setup
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Abort
from ally.design.processor.handler import HandlerProcessor, Handler
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    filters = requires(dict)
    
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    inputs = requires(tuple)
    path = requires(list)
    location = requires(str)

class Element(Context):
    '''
    The element context.
    '''
    # ---------------------------------------------------------------- Required
    node = requires(Context)
    property = requires(TypeProperty)
        
class ACLFilter(Context):
    '''
    The ACL filter context.
    '''
    # ---------------------------------------------------------------- Defined
    targetProperty = defines(TypeProperty, doc='''
    @rtype: TypeProperty
    The target property of the filter.
    ''')
    targets = defines(list, doc='''
    @rtype: list[Context]
    The list of target node contexts.
    ''')
    # ---------------------------------------------------------------- Required
    invokers = requires(list)

# --------------------------------------------------------------------

@injected
@setup(Handler, name='filterTarget')
class FilterTargetHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the filter target property.
    '''
    
    def __init__(self):
        super().__init__(Invoker=Invoker, Element=Element, ACLFilter=ACLFilter)

    def process(self, chain, register:Register, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Provide the filter target.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        if not register.filters: return
        
        aborted = []
        for filter in register.filters.values():
            assert isinstance(filter, ACLFilter), 'Invalid filter %s' % filter
            invalid = False
            for invoker in filter.invokers:
                assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
                for el in invoker.path:
                    assert isinstance(el, Element), 'Invalid element %s' % el
                    if el.property:
                        if filter.targetProperty is None: filter.targetProperty = el.property
                        elif filter.targetProperty != el.property:
                            invalid = True
                            break
                        else:
                            if filter.targets is None: filter.targets = []
                            filter.targets.append(el.node)
                            
            if invalid or not filter.targetProperty:
                if invalid:
                    log.error('Cannot use filters because they have incompatible inputs, at:%s',
                              ''.join(invoker.location for invoker in filter.invokers))
                else:
                    log.error('Cannot use filters because they have no target property, at:%s',
                              ''.join(invoker.location for invoker in filter.invokers))
                aborted.extend(filter.invokers)
                continue
        
        if aborted: raise Abort(*aborted)
