'''
Created on Oct 14, 2013

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the SQL Alchemy session proxy binding.
'''

from inspect import isgenerator
import logging

from ally.container.impl.proxy import IProxyHandler, Execution, \
    registerProxyHandler, hasProxyHandler
from ally.container.ioc import injected
from ally.design.processor.attribute import requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from sql_alchemy.support.session import beginWith, endCurrent, rollback, \
    hasSession, openSession, commit


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Bind(Context):
    '''
    The bind context.
    '''
    # ---------------------------------------------------------------- Required
    proxy = requires(object)
    
# --------------------------------------------------------------------

@injected
class BindSessionHandler(HandlerProcessor, IProxyHandler):
    '''
    Implementation for a processor that provides the SQL Alchemy session proxy binding.
    '''
    
    sessionCreator = None
    # The session creator used for creating SQL Alchemy sessions.
    
    def __init__(self):
        assert self.sessionCreator is not None, 'Required a session creator'
        super().__init__()

    def process(self, chain, bind:Bind, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Binds a session creator wrapping for the provided proxy.
        '''
        assert isinstance(bind, Bind), 'Invalid bind %s' % bind
        assert not hasProxyHandler(BindSessionHandler, bind.proxy), 'Proxy already has a session %s' % bind.proxy

        registerProxyHandler(self, bind.proxy)

    # ----------------------------------------------------------------

    def handle(self, execution):
        '''
        @see: IProxyHandler.handle
        '''
        assert isinstance(execution, Execution), 'Invalid execution %s' % execution

        beginWith(self.sessionCreator)
        try: returned = execution.invoke()
        except:
            endCurrent(rollback)
            raise
        else:
            if hasSession():
                session = openSession()
                try:
                    session.flush()
                    session.expunge_all()
                    endCurrent(commit)
                except:
                    endCurrent(rollback)
                    raise
            else:
                endCurrent(commit) # Since there is no session there will be nothing to commit, we just make sure here
                # that the session creator has been removed from q.
                if isgenerator(returned):
                    # If the returned value is a generator we need to wrap it in order to provide session support when the actual
                    # generator is used
                    return self.wrapGenerator(returned)

            return returned

    # ----------------------------------------------------------------

    def wrapGenerator(self, generator):
        '''
        Wraps the generator with the session creator.
        '''
        assert isgenerator(generator), 'Invalid generator %s' % generator
        beginWith(self.sessionCreator)
        try:
            for item in generator: yield item
        except:
            endCurrent(rollback)
            raise
        else:
            endCurrent(commit)
