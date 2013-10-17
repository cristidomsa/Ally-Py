'''
Created on Oct 16, 2013

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the proxy binder for SQL alchemy.
'''

import logging

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Processing


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Bind(Context):
    '''
    The bind context.
    '''
    # ---------------------------------------------------------------- Defined
    proxy = defines(object)
    
# --------------------------------------------------------------------

@injected
class BinderHandler:
    '''
    Implementation for a processor that provides the SQL Alchemy session proxy binding.
    '''
    
    bindAssembly = Assembly
    # The assembly used for binding.
    
    def __init__(self):
        assert isinstance(self.bindAssembly, Assembly), 'Invalid assembly %s' % self.bindAssembly
        
        self._processor = self.bindAssembly.create(bind=Bind)
        
    def bind(self, proxy):
        '''
        Binds the SQL alchemy to the provided proxy.
        '''
        proc = self._processor
        assert isinstance(proc, Processing), 'Invalid processing %s' % proc
        
        proc.execute(bind=proc.ctx.bind(proxy=proxy))
        
