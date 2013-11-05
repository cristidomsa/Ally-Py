
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
     url='http://www.sourcefabric.org/en/superdesk/', # project home page     description='Provides the HTTP asyncore server',
     author='Gabriel Nistor',
     install_requires=['ally-http >= 1.0'],
     long_description='Provides an HTTP server substitute for the basic server from ally-http \nthat handles the requests in an asyncore manner by using the python built in asyncore package.',
     author_email='gabriel.nistor@sourcefabric.org',
     version='1.0',
     test_suite='__unit_test__',
     keywords=['Ally', 'REST', 'HTTP', 'asyncore', 'server'],
     classifiers=['Development Status :: 4 - Beta'],
     name='ally-http-asyncore-server',

     )