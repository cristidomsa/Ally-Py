
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

setup(name='security',
author='Ioan Pocol',
install_requires=['ally-api >= 1.0', 'support-sqlalchemy >= 1.0'],
author_email=('gabriel.nistor@sourcefabric.org',),
version='1.0',
keywords=['Ally', 'REST', 'plugin', 'support', 'security'],
description='This plugin provides the basic security models.',
packages=find_packages('.'),
      platforms=['all'],
      zip_safe=True,
      license='GPL v3',
      url='http://www.sourcefabric.org/en/superdesk/', # project home page
      )
