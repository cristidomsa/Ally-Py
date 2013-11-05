'''
Created on Jul 15, 2011

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Contains ally base setup files.
'''

# --------------------------------------------------------------------

NAME = 'ally'
VERSION = '1.0'
DESCRIPTION = 'Ally framework - utilities component'
AUTHOR = 'Gabriel Nistor'
AUTHOR_EMAIL = 'gabriel.nistor@sourcefabric.org'
KEYWORDS = ['Ally', 'REST']
INSTALL_REQUIRES = ['httplib2==0.7.7', 
                    'Jinja2==2.6',
                    'PyYAML==3.10',
                    'SQLAlchemy==0.7.1',
                    'sunburnt==0.6',
                    'lxml==3.0']
LONG_DESCRIPTION = '''This is the main component and is the application entry point. 
'This component provides also support for inversion of control container.
'Basically this component contains general support for the application that is not in any way linked with a particular technology.'''
TEST_SUITE = '__unit_test__'
CLASSIFIERS = ['Development Status :: 4 - Beta']
__extra__ = dict(py_modules = ['application', 'package_extender'],
                 dependency_links = ["https://github.com/sourcefabric/Ally-Py/tree/master/distribution/libraries"])