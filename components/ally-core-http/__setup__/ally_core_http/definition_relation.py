'''
Created on Jul 14, 2013

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the relation definitions.
'''


from ally.container import ioc
from ally.core.http.impl.definition import Relation

from ..ally_core.definition import descriptions, desc


# --------------------------------------------------------------------
@ioc.before(descriptions)
def updateDescriptionsForRelation():
    desc(Relation(), 'the provided value needs to be available at \'%(path)s\'', path=Relation())
