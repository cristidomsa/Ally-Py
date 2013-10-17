'''
Created on Oct 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC support for application deploy.
'''

from ally.design.priority import PRIORITY_NORMAL, Priority
from ally.support.util_sys import callerLocals

from ._impl._assembly import Assembly
from ._impl._setup import SetupConfig
from .context import activate
from .event import onDecorator, Trigger
from .support import force
from ally.container._impl._call import CallConfig


# --------------------------------------------------------------------
APP_PREPARE = Trigger('application prepare')
# Trigger used for controlled event on preparing the application arguments.
APP_START = Trigger('application start') 
# Trigger used for controlled event on application start.

# --------------------------------------------------------------------

def prepare(priority=PRIORITY_NORMAL):
    '''
    Decorator for application prepare setup functions. The prepare function will be called mainly in order to prepare
    the application arguments.
    
    @param priority: one of priority markers
        The priority to associate with the event.
    '''
    if isinstance(priority, Priority): return onDecorator((APP_PREPARE,), priority, callerLocals())
    return onDecorator((APP_PREPARE,), PRIORITY_NORMAL, callerLocals())(priority)

def start(priority=PRIORITY_NORMAL):
    '''
    Decorator for application start setup functions. The start function will be called after the application arguments
    have been parsed.
    
    @param priority: one of priority markers
        The priority to associate with the event.
    '''
    if isinstance(priority, Priority): return onDecorator((APP_START,), priority, callerLocals())
    return onDecorator((APP_START,), PRIORITY_NORMAL, callerLocals())(priority)

# --------------------------------------------------------------------

class Options:
    '''
    Provides the container for arguments options.
    '''
    
    def __init__(self):
        '''
        Construct the options.
        '''
        self._flagsRegistered = {}
        self._flagsLinked = {}
        self._flags = set()
        self._configurations = {}
        
    def registerFlag(self, name, *invalidate):
        '''
        Register a flag with the provided name that is by default False.
        
        @param name: string
            The flag name to register.
        @param invalidate: arguments[string]
            The flag names to invalidate (set to False) if this flag is set to True.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        if __debug__:
            for fname in invalidate: assert isinstance(fname, str), 'Invalid invalidate flag name %s' % fname
        self._flagsRegistered[name] = invalidate
        
    def registerFlagTrue(self, name, *invalidate):
        '''
        Register a flag with the provided name that is by default True.
        
        @param name: string
            The flag name to register.
        @param invalidate: arguments[string]
            The flag names to invalidate (set to False) if this flag is set to True.
        '''
        self.registerFlag(name)
        self._flags.add(name)
        
    def registerFlagLink(self, name, *flags, value=True):
        '''
        Register a flag link with a provided property name.
        
        @param name: string
            The property name that if is set then it will trigger the linked flags to be placed with the provided value.
        @param value: boolean
            The status to set on the linked flags.
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        assert flags, 'At least one flag is required'
        assert isinstance(value, bool), 'Invalid value to set on the flags %s' % value
        if __debug__:
            for fname in flags: assert isinstance(fname, str), 'Invalid flag name %s' % fname 
            
        current = self._flagsLinked.get(name)
        if current is None: current = self._flagsLinked[name] = [], []
        flagsTrue, flagsFalse = current
        
        if value: flagsTrue.extend(flags)
        else: flagsFalse.extend(flags)
        
    def registerConfiguration(self, setup, assembly=None):
        '''
        Register a setup configuration as an option.
        
        @param setup: SetupConfig
            The configuration setup to place the value to.
        @param assembly: Assembly|None
            The assembly used for setting the setup in.
        @return: string
            The name under which the setup is registered.
        '''
        assert isinstance(setup, SetupConfig), 'Invalid configuration setup %s' % setup
        assert assembly is None or isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
        name = setup.name.replace('.', '_').lstrip('_')
        self._configurations[name] = (setup, assembly)
        return name
    
    def isFlag(self, name):
        '''
        Checks if the flag is set.
        
        @param name: string
            The flag name to check.
        @return: boolean
            True if the flag is set, False otherwise
        '''
        assert isinstance(name, str), 'Invalid name %s' % name
        return name in self._flags
    
    def __getattr__(self, name):
        if not name.startswith('_'):
            if name in self._configurations:
                setup, assembly = self._configurations[name]
                assert isinstance(setup, SetupConfig), 'Invalid configuration setup %s' % setup
                if not assembly and Assembly.stack: assembly = Assembly.current()
                if not assembly: return
                assert isinstance(assembly, Assembly)
                call = assembly.fetchForName(setup.name)
                if not call: return
                assert isinstance(call, CallConfig), 'Invalid call %s' % call
                return call.value
        return object.__getattr__(self, name)
    
    def __setattr__(self, name, value):
        assert isinstance(name, str), 'Invalid name %s' % name
        if name.startswith('_'): object.__setattr__(self, name, value)
        else:
            if name in self._flagsRegistered:
                if value:
                    self._flags.difference_update(self._flagsRegistered[name])
                    self._flags.add(name)
                else: self._flags.discard(name)
            elif name in self._configurations:
                if value is not None:
                    setup, assembly = self._configurations[name]
                    if assembly:
                        with activate(assembly, 'set configuration'): force(setup, value)
                    else: force(setup, value)
            else: object.__setattr__(self, name, value)
            
            if name in self._flagsLinked:
                flagsTrue, flagsFalse = self._flagsLinked[name]
                for flag in flagsTrue:
                    self._flags.difference_update(self._flagsRegistered[flag])
                    self._flags.add(flag)
                for flag in flagsFalse: self._flags.discard(flag)
            
