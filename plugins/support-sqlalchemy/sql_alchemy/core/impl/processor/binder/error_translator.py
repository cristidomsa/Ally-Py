'''
Created on Oct 14, 2013

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the translation of SQL Alchemy errors to proper API input errors.
'''

from collections import Iterable
import logging
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from ally.api.config import DELETE, GET
from ally.api.error import InputError, IdError
from ally.api.operator.type import TypeService, TypeCall, TypeModel
from ally.api.type import typeFor
from ally.container.impl.proxy import IProxyHandler, Execution, hasProxyHandler, \
    registerProxyHandler, ProxyCall, ProxyMethod
from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines, requires
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing, FILL_ALL
from ally.design.processor.handler import HandlerProcessor
from ally.internationalization import _


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Bind(Context):
    '''
    The bind context.
    '''
    # ---------------------------------------------------------------- Required
    proxy = requires(object)
    
class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Defined
    services = defines(Iterable, doc='''
    @rtype: Iterable(class)
    The classes that implement service APIs.
    ''')
    # ---------------------------------------------------------------- Required
    invokers = requires(list)
    
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Required
    call = requires(TypeCall)
    method = requires(int)
    target = requires(TypeModel)

# --------------------------------------------------------------------

@injected
class ErrorTranslatorHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the translation of SQL Alchemy errors to proper API input errors.
    '''
    
    assembly = Assembly
    # The assembly used for handling the required error translation data.
    
    def __init__(self):
        assert isinstance(self.assembly, Assembly), 'Invalid assembly %s' % self.assembly
        super().__init__()
        
        self._processing = self.assembly.create(register=Register, Invoker=Invoker)

    def process(self, chain, bind:Bind, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Wraps the invoking and all processors after in a single transaction.
        '''
        assert isinstance(bind, Bind), 'Invalid bind %s' % bind
        if not isinstance(typeFor(bind.proxy), TypeService): return
        
        proc = self._processing
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        arg = proc.execute(FILL_ALL, register=proc.ctx.register(services=[bind.proxy]))
        assert isinstance(arg.register, Register), 'Invalid register %s' % arg.register
        if not arg.register.invokers: return
        assert not hasProxyHandler(ProxyTransalator, bind.proxy), 'Proxy already has a session %s' % bind.proxy
        
        invokers = {}
        for invoker in arg.register.invokers:
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            assert isinstance(invoker.call, TypeCall), 'Invalid call %s' % invoker.call
            invokers[invoker.call.name] = invoker
        
        if invokers: registerProxyHandler(ProxyTransalator(invokers), bind.proxy)

# --------------------------------------------------------------------

class ProxyTransalator(IProxyHandler):
    '''
    Implementation @see: IProxyHandler that translates errors.
    '''
    
    def __init__(self, invokers):
        '''
        Construct the translator based on the invokers.
        '''
        assert isinstance(invokers, dict), 'Invalid invokers %s' % invokers
        
        self.invokers = invokers

    def handle(self, execution):
        '''
        @see: IProxyHandler.handle
        '''
        assert isinstance(execution, Execution), 'Invalid execution %s' % execution
        assert isinstance(execution.proxyCall, ProxyCall), 'Invalid proxy call %s' % execution.proxyCall
        assert isinstance(execution.proxyCall.proxyMethod, ProxyMethod), \
        'Invalid proxy method %s' % execution.proxyCall.proxyMethod
        
        invoker = self.invokers.get(execution.proxyCall.proxyMethod.name)
        if not invoker: return execution.invoke()
        
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        
        try: return execution.invoke()
        except SQLAlchemyError as exc:
            iexc = None
            
            if isinstance(exc, NoResultFound):
                iexc = IdError()
            
            elif isinstance(exc, IntegrityError):
                iexc = InputError(_('There is already an entity having this unique properties'))
                
            elif isinstance(exc, OperationalError):
                if invoker.method == DELETE: iexc = InputError(_('Cannot delete because is used'))
                elif invoker.method != GET: iexc = InputError(_('An entity relation identifier is not valid'))
            
            if iexc is not None:
                if invoker.target: iexc.update(invoker.target)
                log.info('SQL Alchemy handled exception occurred', exc_info=(type(exc), exc, exc.__traceback__))
                iexc.with_traceback(exc.__traceback__)
                exc = iexc
            else: log.warn('Unknown SQL Alchemy error', exc_info=(type(exc), exc, exc.__traceback__))
                
            raise exc
