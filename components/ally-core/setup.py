
'''
Created on Oct 1, 2013
 
@package: distribution_manager
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Setup configuration for components/plugins needed for pypi.
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(packages=find_packages('.'),
     platforms=['all'],
     zip_safe=True,
     license='GPL v3',
     url='http://www.sourcefabric.org/en/superdesk/', # project home page     description='Provides the core functionality for handling the REST API decorated services and models',
     author='Gabriel Nistor',
     install_requires=['ally-api >= 1.0', 'ally-indexing >= 1.0'],
     long_description='Provides the general support for handling the [API] services that have been decorated as [REST] services.',
     author_email='gabriel.nistor@sourcefabric.org',
     version='1.0',
     test_suite='__unit_test__',
     keywords=['Ally', 'core', 'REST'],
     classifiers=['Development Status :: 4 - Beta'],
     name='ally-core',

     )