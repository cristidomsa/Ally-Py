'''
Created on Oct 14, 2013
 
@package: support cdm
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Cristian Domsa
 
Configuration for cdm service
'''

from os import path

from ally.cdm.impl.local_filesystem import IDelivery, HTTPDelivery, LocalFileSystemCDM
from ally.cdm.spec import ICDM
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.config
def server_uri():
    ''' The HTTP server URI, basically the URL where the content should be fetched from'''
    return '/content/'

@ioc.config
def repository_path():
    ''' The repository absolute or relative (to the distribution folder) path '''
    return path.join('workspace', 'shared', 'cdm')

@ioc.config
def use_linked_cdm():
    ''' Set to true when the files should not be copied into cdm'''
    return True

# --------------------------------------------------------------------
# Creating the content delivery managers

@ioc.entity
def delivery() -> IDelivery:
    d = HTTPDelivery()
    d.serverURI = server_uri()
    d.repositoryPath = repository_path()
    return d

@ioc.entity
def contentDeliveryManager() -> ICDM:
    cdm = LocalFileSystemCDM()
    cdm.delivery = delivery()
    return cdm
