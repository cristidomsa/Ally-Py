'''
Created on Jan 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the setup assembly implementations for the IoC module.
'''

from ..error import SetupError, ConfigError
from collections import deque
from inspect import ismodule
import abc
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Setup(metaclass=abc.ABCMeta):
    '''
    The setup entity. This class provides the means of indexing setup Callable objects.
    '''

    priority_index = 1
    # Provides the indexing priority for the setup.
    priority_assemble = 1
    # Provides the assemble priority for the setup.

    def index(self, assembly):
        '''
        Indexes the call of the setup and other data.
        
        @param assembly: Assembly
            The assembly to index on.
        '''

    def assemble(self, assembly):
        '''
        Assemble the calls map and also add the call starts. This method will be invoked after all index methods have
        been finalized.
        
        @param assembly: Assembly
            The assembly to assemble additional behavior on.
        '''
    
    @abc.abstractmethod
    def __str__(self):
        '''
        Representation for setup function.
        '''
        
# --------------------------------------------------------------------

class Assembly:
    '''
    Provides the assembly data.
    '''

    stack = []
    # The current assemblies stack.

    @classmethod
    def current(cls):
        '''
        Provides the current assembly.
        
        @return: Assembly
            The current assembly.
        @raise SetupError: if there is no current assembly.
        '''
        if not cls.stack: raise SetupError('There is no active assembly to process on')
        return cls.stack[-1]

    @classmethod
    def process(cls, name):
        '''
        Process the specified name into the current active context.
        
        @param name: string
            The name to be processed.
        '''
        ass = cls.current()
        assert isinstance(ass, Assembly), 'Invalid assembly %s' % ass
        return ass.processForName(name)

    def __init__(self):
        '''
        Construct the assembly.
        
        @ivar configUsed: set{string}
            A set containing the used configurations names from the external configurations.
        @ivar calls: dictionary{string, Callable}
            A dictionary containing as a key the name of the call to be resolved and as a value the Callable that will
            resolve the name. The Callable will not take any argument.
        @ivar callsOfValue: dictionary{intege:list[Callable]}
            A dictionary containing the calls for a value, the value id is used as a key.
        @ivar called: set[string]
            A set of the called calls in this assembly.
        '''
        self.calls = {}
        self.callsOfValue = {}
        self.called = set()
        self.setups = []
        
        self._setupsToIndex = []
        self._setupsToAssemble = []
        self._processing = deque()
        
    def addSetupModule(self, module):
        '''
        Adds a new setup module to the assembly.
        
        @param module: module
            The setup module.
        '''
        assert ismodule(module), 'Invalid module setup %s' % module
        try: module.__ally_setups__
        except AttributeError: log.info('No setup found in %s', module)
        else: self._setupsToIndex.extend(module.__ally_setups__)
    
    def index(self):
        '''
        Index into this assembly the pending index setups.
        
        @return: self
            The self instance for chaining purposes.
        '''
        if self._setupsToIndex:
            for setup in sorted(self._setupsToIndex, key=lambda setup: setup.priority_index): setup.index(self)
            self._setupsToAssemble = self._setupsToIndex
            self._setupsToIndex = []
        return self
    
    def assemble(self):
        '''
        Assembles into this assembly the pending setups.
        
        @return: self
            The self instance for chaining purposes.
        '''
        if self._setupsToAssemble:
            for setup in sorted(self._setupsToAssemble, key=lambda setup: setup.priority_assemble): setup.assemble(self)
            self.setups = self._setupsToAssemble
            self._setupsToAssemble = []

        return self

    def fetchForName(self, name):
        '''
        Fetch the call with the specified name.
        
        @param name: string
            The name of the call to be fetched.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        call = self.calls.get(name)
        if not call: raise SetupError('No IoC resource for name \'%s\', possible reasons:\n\t- the setup function you '
        'are calling is not registered in the current assembly\n\t- you have added an \'after\' or \'before\' event to '
        'a setup function that is from a different assembly\n\t  and when the event is triggered the setup function assembly '
        'is no longer available' % name)
        if not callable(call): raise SetupError('Invalid call %s for name \'%s\'' % (call, name))
        return call

    def processForName(self, name):
        '''
        Process the specified name into this assembly.
        
        @param name: string
            The name to be processed.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        self._processing.append(name)
        try: value = self.fetchForName(name)()
        except (SetupError, ConfigError, SystemExit): raise
        except: raise SetupError('Exception occurred for %r in processing chain \'%s\'' % 
                                 (name, ', '.join(self._processing)))
        self._processing.pop()
        return value

class Activator:
    ''' Provides the activate assembly to be used with ``with`` for an opened assembly
    to ensure closing and error reporting. '''
    
    def __init__(self, assembly, reason):
        '''
        Create the watcher.
        
        :param assembly: The assembly to activate
        :type action: Assembly.
        
        :param reason: The reason name to associate with the assembly.
        :type reason: str.
        '''
        assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        assert isinstance(reason, str), 'Invalid reason %s' % reason
        
        self.assembly = assembly
        self.reason = reason
        
    def __enter__(self):
        Assembly.stack.append(self.assembly)
        return self.assembly
        
    def __exit__(self, type, value, tb):
        assert Assembly.stack, 'No assembly available for deactivation'
        Assembly.stack.pop()
        
        if not isinstance(value, Exception): return
        if isinstance(value, SystemExit): return
        if isinstance(value, (SetupError, ConfigError)):
            log.error('-' * 150)
            log.exception('A setup or configuration error occurred, rebuilding the configurations might help.')
            log.error('-' * 150)
        else:
            log.error('-' * 150)
            log.exception('A problem occurred while %s.', self.reason)
            log.error('-' * 150)
        return True
