
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
     url='http://www.sourcefabric.org/en/superdesk/', # project home page     package_data={'': ['*.txt', '*.conf']},
     description='Provides the HTTP mongrel2 server',
     author='Gabriel Nistor',
     install_requires=['ally-http >= 1.0'],
     long_description='Similar to the asyncore server but provides support for using \n0MQ messaging in order to communicate with Mongrel2 HTTP server.',
     author_email='gabriel.nistor@sourcefabric.org',
     version='1.0',
     test_suite='__unit_test__',
     keywords=['Ally', 'REST', 'HTTP,mongrel2', 'server'],
     classifiers=['Development Status :: 4 - Beta'],
     name='ally-http-mongrel2-server',

     )