'''
Created on Jan 17, 2012

@package: gateway acl
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the database settings.
'''

from ..sql_alchemy.db_application import metas, bindApplicationSession
from acl.meta.metadata_acl import meta
from ally.container import ioc

# --------------------------------------------------------------------

@ioc.entity
def binders(): return [bindApplicationSession]

# --------------------------------------------------------------------

@ioc.before(metas)
def updateMetasForACL(): metas().append(meta)
