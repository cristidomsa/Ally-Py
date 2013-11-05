'''
Created on Sep 26, 2013

@author: mihaigociu
'''
import logging

from ally.container.ioc import injected
from ally.design.processor.assembly import Assembly
from ally.design.processor.attribute import defines
from ally.design.processor.context import Context
from ally.design.processor.execution import FILL_ALL
from ally.support.util_io import IInputStream
from ally.notifier.impl.processor.register import RegisterListeners

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class SolicitScan(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Defines
    stream = defines(IInputStream, doc='''
    @rtype: IInputStream
    The input stream to to scan.
    ''')
    uri = defines(str, doc='''
    @rtype: string
    The corresponding URI of the given stream.
    ''')

# --------------------------------------------------------------------

@injected
class ConfigurationListeners(RegisterListeners):
    
    assemblyConfiguration = Assembly
    
    def __init__(self):
        assert isinstance(self.assemblyConfiguration, Assembly), 'Invalid assembly %s' % self.assemblyConfiguration
        super().__init__()
        
        self._processing = self.assemblyConfiguration.create(solicit=SolicitScan)
    
    def doOnContentChanged(self, uri, content):
        '''
        @see: RegisterListeners.doOnContentChanged
        '''
        if content == None: assert log.debug('Deleted content for URI: %s' % uri) or True
        else:
            assert isinstance(content, IInputStream) or content is None, 'Invalid content stream %s' % content
            assert log.debug('Parsing content for URI: %s' % uri) or True
        
        solicit = self._processing.ctx.solicit(stream=content, uri=uri)
        self._processing.execute(FILL_ALL, solicit=solicit)
        solicit
