'''
Created on June 14, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor
'''

# --------------------------------------------------------------------

from setuptools import setup, find_packages

# --------------------------------------------------------------------

setup(
    name='ally_http_proxy_server',
    version='1.0',
    packages=find_packages(),
    install_requires=['ally_core_http >= 1.0'],
    platforms=['all'],
    test_suite='test',
    zip_safe=True,

    # metadata for upload to PyPI
    author='Gabriel Nistor',
    author_email='gabriel.nistor@sourcefabric.org',
    description='Ally framework - HTTP server that uses proxied instance for processing',
    long_description='Provides a server extension that runs on multiple processors',
    license='GPL v3',
    keywords='Ally REST framework',
    url='http://www.sourcefabric.org/en/superdesk/',  # project home page
)
