'''
Created on Jan 5, 2012

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides automatic session handling for SQL alchemy in ally core.
'''

import logging

from ally.api.error import InputError
from ally.core.spec.codes import Coded
from ally.design.processor.attribute import optional, defines
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor
from sql_alchemy.support.session import rollback, commit, setKeepAlive, \
    endSessions


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------
    
class Response(Coded):
    '''
    The response context.
    '''
    # ---------------------------------------------------------------- Defined
    errorInput = defines(InputError, doc='''
    @rtype: InputError
    The input error translated from SQL alchemy error.
    ''')
    # ---------------------------------------------------------------- Optional
    isSuccess = optional(bool)

# --------------------------------------------------------------------

class TransactionCoreHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the SQLAlchemy session handling in ally core.
    '''
    
    def __init__(self):
        super().__init__(response=Response)

    def process(self, chain, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Wraps the invoking and all processors after in a single transaction.
        '''
        assert isinstance(chain, Chain), 'Invalid processors chain %s' % chain

        setKeepAlive(True)
        chain.onFinalize(self.processFinalize)
    
    def processFinalize(self, final, response, **keyargs):
        '''
        Process the finalize of the transaction.
        '''
        assert isinstance(response, Response), 'Invalid response %s' % response
        setKeepAlive(False)
        
        if Response.isSuccess in response:
            if response.isSuccess is True: endSessions(commit)
            else: endSessions(rollback)
        else: endSessions(commit)  # Commit if there is no success flag
            
