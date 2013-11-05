
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
     url='http://www.sourcefabric.org/en/superdesk/', # project home page     package_data={'': ['*.zip']},
     description='Provides the content delivery manager and support for handling it',
     author='Gabriel Nistor',
     install_requires=['ally-http >= 1.0'],
     long_description='This component provide the content delivery management, basically the static resources streaming \nsince REST is only for models, usually the REST models will have references to static files, like media files and \nthe CDM is used for delivery them.',
     author_email='gabriel.nistor@sourcefabric.org',
     version='1.0',
     test_suite='__unit_test__',
     keywords=['Ally', 'REST', 'Content', 'manager', 'service'],
     classifiers=['Development Status :: 4 - Beta'],
     name='service-cdm',

     )