'''
Created on May 28, 2013

@package: ally core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the processing on callers based on methods.
'''

from ally.api.config import GET, INSERT, UPDATE, DELETE
from ally.api.operator.type import TypeProperty, TypeModel
from ally.api.type import Iter, Type
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Required
    invokers = requires(list)
    
class Invoker(Context):
    '''
    The invoker context.
    '''
    # ---------------------------------------------------------------- Defined
    target = defines(TypeModel, doc='''
    @rtype: TypeModel
    The target model of the caller.
    ''')
    isCollection = defines(bool, doc='''
    @rtype: boolean
    If True it means that the invoker provides a collection.
    ''')
    isModel = defines(bool, doc='''
    @rtype: boolean
    If True it means that the invoker provides a full model, attention the model can be in a collection.
    ''')
    # ---------------------------------------------------------------- Required
    method = requires(int)
    inputs = requires(tuple)
    output = requires(Type)
    location = requires(str)
    
# --------------------------------------------------------------------

class ProcessMethodHandler(HandlerProcessor):
    '''
    Implementation for a processor that provides the inputs and output processing and validation based on the method.
    '''
    
    def __init__(self):
        super().__init__(Invoker=Invoker)

    def process(self, chain, register:Register, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Process the invokers based on method.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        if not register.invokers: return  # No invokers to process.
        
        assert isinstance(register.invokers, list), 'Invalid invokers %s' % register.invokers
        k = 0
        while k < len(register.invokers):
            invoker = register.invokers[k]
            k += 1
            assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
            
            if invoker.method == GET: keep = self.processGET(invoker)
            elif invoker.method == INSERT: keep = self.processINSERT(invoker)
            elif invoker.method == UPDATE: keep = self.processUPDATE(invoker)
            elif invoker.method == DELETE: keep = self.processDELETE(invoker)
            else:
                log.error('Cannot use because the method %s is not known, at:%s', invoker.method, invoker.location)
                keep = False
            
            if not keep:
                k -= 1
                del register.invokers[k]

    # ----------------------------------------------------------------
    
    def processGET(self, invoker):
        '''
        Process the GET invoker, returns True if the invoker should be kept.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker
        
        if isinstance(invoker.output, Iter):
            assert isinstance(invoker.output, Iter)
            output = invoker.output.itemType
            invoker.isCollection = True
        else:
            output = invoker.output
            
        if isinstance(output, TypeProperty):
            assert isinstance(output, TypeProperty)
            output = output.parent
        else: invoker.isModel = True

        if isinstance(output, TypeModel):
            invoker.target = output
            return True
        
        log.error('Cannot use because the output %s is not for a model, at:%s', invoker.output, invoker.location)
        
    def processINSERT(self, invoker):
        '''
        Process the INSERT invoker, returns True if the invoker should be kept.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        output = invoker.output
        if isinstance(output, TypeProperty):
            assert isinstance(output, TypeProperty)
            output = output.parent

        if isinstance(output, TypeModel):
            invoker.target = output
            return True
        
        log.error('Cannot use because the output %s is not for a model, at:%s', invoker.output, invoker.location)
 
    def processUPDATE(self, invoker):
        '''
        Process the UPDATE invoker, returns True if the invoker should be kept.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        models = [inp.type for inp in invoker.inputs if isinstance(inp.type, TypeModel)]
        if len(models) > 1:
            log.error('Cannot use because there are to many models %s to insert, at:%s',
                     ', '.join(str(model) for model in models), invoker.location)
            return False
        elif models: invoker.target = models[0]
        return True
    
    def processDELETE(self, invoker):
        '''
        Process the DELETE invoker, returns True if the invoker should be kept.
        '''
        assert isinstance(invoker, Invoker), 'Invalid invoker %s' % invoker

        if not invoker.output.isOf(bool):
            log.error('Cannot use because a boolean return is expected, at:%s', invoker.location)
            return False
        return True
