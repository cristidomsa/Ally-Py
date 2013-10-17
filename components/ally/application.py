'''
Created on Jan 23, 2013

@package: ally base
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

The entry point module that starts the application.
'''

import argparse
import sys
import timeit
import traceback


# --------------------------------------------------------------------
try:
    import package_extender
    package_extender.PACKAGE_EXTENDER.addFreezedPackage('__setup__.')
    from ally.container import aop, context, support
    from ally.container.deploy import Options, APP_PREPARE, APP_START
except ImportError:
    print('Corrupted or missing ally component, make sure that this component is not missing from python path '
          'or components eggs', file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)
    
# --------------------------------------------------------------------

parser = argparse.ArgumentParser(description='ally-py application options.')  # The parser to be prepared.
options = Options()

# --------------------------------------------------------------------

def __deploy__():
    # Deploy the application
    with context.activate(context.open(aop.modulesIn('__setup__.**')), 'deploy'):
        support.performEventsFor(APP_PREPARE)
        # In the second stage we parse the application arguments.
        parser.parse_args(namespace=options)
    
        support.performEventsFor(APP_START)

if __name__ == '__main__':
    sys.modules['application'] = sys.modules['__main__']
    deployTime = timeit.timeit(__deploy__, number=1)
    print('=' * 50, 'Application deployed in %.2f seconds' % deployTime)
