'''
Created on Jan 8, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the IoC deployment operations.
'''

import importlib
from inspect import ismodule
import logging

from ally.design.priority import sortByPriorities

from ._impl._aop import AOPModules
from ._impl._assembly import Assembly, Activator
from ._impl._call import CallConfig
from ._impl._setup import CallStart
from .error import SetupError
from .impl.config import Config


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

def open(*modules, included=False):
    '''
    Load and assemble the setup modules and keeps them opened for retrieving and processing values. Call the close
    function after finalization. Automatically activates the assembly.
    
    @param modules: arguments(path|AOPModules|module) 
        The modules that compose the setup.
    @param config: dictionary|None
        The configurations dictionary. This is the top level configurations the values provided here will override any
        other configuration.
    @param included: boolean
        Flag indicating that the newly opened assembly should include the currently active assembly, if this flag is
        True then the opened assembly will have access to the current assembly.
    @return: Assembly
        The assembly object.
    '''
    assert isinstance(included, bool), 'Invalid included flag %s' % included
    
    assembly = Assembly()
    for module in modules:
        if isinstance(module, str): module = importlib.import_module(module)

        if ismodule(module): assembly.addSetupModule(module)
        elif isinstance(module, AOPModules):
            assert isinstance(module, AOPModules)
            for m in module.load().asList(): assembly.addSetupModule(m)
        else: raise SetupError('Cannot use module %s' % module)
    
    if included: assembly.calls.update(Assembly.current().calls)
    return assembly.index().assemble()

def activate(assembly, reason):
    '''
    Activates the provided assembly.
    
    @param assembly: Assembly
        The assembly to activate.
    @param action: string
        The activate reason.
    @return: Activator
        The activator to use for save assembly processing.
    '''
    return Activator(assembly, reason)

def processStart(assembly=None):
    '''
    Process in the assembly the start calls.
    
    @param assembly: Assembly|None
        The assembly to process the start for, if None the active assembly will be used.
    '''
    assembly = assembly or Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
    
    calls = []
    for call in assembly.calls.values():
        if isinstance(call, CallStart):
            assert isinstance(call, CallStart)
            if call.assembly == assembly: calls.append(call)
    sortByPriorities(calls, priority=lambda call: call.priority)
    for call in calls: assembly.processForName(call.name)
    
def configurationsExtract(assembly=None):
    '''
    Provides the configurations for the assembly.
    
    @param assembly: Assembly|None
        The assembly to provide configurations for, if None the active assembly will be used.
    @return: dictionary{string: Config}
        The extracted configurations.
    '''
    if assembly is None: assembly = Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
    
    configurations = {}
    Assembly.stack.append(assembly)
    try:
        for name, call in assembly.calls.items():
            if not isinstance(call, CallConfig): continue
            if not call.assembly == assembly: continue
            assert isinstance(call, CallConfig)
            configurations[name] = call.config()
    
    finally: Assembly.stack.pop()
    
    def expand(name, sub):
        ''' Used for expanding configuration names'''
        if sub: root = name[:-len(sub)]
        else: root = name
        if not root: return name
        if root[-1] == '.': root = root[:-1]
        k = root.rfind('.')
        if k < 0: return name
        if sub: return root[k + 1:] + '.' + sub
        return root[k + 1:]

    configs, expanded = {}, set()
    for name, config in configurations.items():
        assert isinstance(config, Config), 'Invalid configuration %s' % config
        sname = name[len(config.group) + 1:]
        other = configs.pop(sname, None)
        while other or sname in expanded:
            if other:
                assert isinstance(other, Config)
                configs[expand(other.name, sname)] = other
                expanded.add(sname)
            sname = expand(name, sname)
            other = configs.pop(sname, None)
        configs[sname] = config
        
    return configs

def configurationsLoad(configs, assembly=None):
    '''
    Updates the configurations for the assembly.
    
    @param configs: dictionary{string: object}
        The configurations to update the assembly with.
    @param assembly: Assembly|None
        The assembly to update configurations for, if None the active assembly will be used.
    '''
    assert isinstance(configs, dict), 'Invalid configurations %s' % configs
    if assembly is None: assembly = Assembly.current()
    assert isinstance(assembly, Assembly), 'Invalid assembly %s' % assembly
    
    used = set()
    Assembly.stack.append(assembly)
    try:
        for name, call in assembly.calls.items():
            if not isinstance(call, CallConfig): continue
            assert isinstance(call, CallConfig)
            
            for name, value in configs.items():
                if name == call.name or call.name.endswith('.' + name):
                    if name in used:
                        raise SetupError('The configuration "%s" is already in use and the configuration "%s" cannot use it '
                                         'again, provide a more detailed path for the configuration (ex: "ally_core.url" '
                                         'instead of "url")' % (name, call.name))
                    used.add(name)
                    call.setValue(value)
                    
    finally: Assembly.stack.pop()
    
    unused = set(configs)
    unused.difference_update(used)
    if unused: log.info('Unknown configurations: %s', ', '.join(unused))
