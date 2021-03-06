'''
Created on Dec 21, 2012

@package: security
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Ioan v. Pocol

Contains the SQL alchemy meta for right API.
'''

from ..api.right import Right
from .metadata_security import Base
from .right_type import RightTypeMapped
from acl.meta.acl import WithAclAccess
from acl.meta.compensate import WithCompensate
from sql_alchemy.support.util_meta import relationshipModel
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String

# --------------------------------------------------------------------

class RightMapped(Base, Right):
    '''
    Provides the mapping for Right.
    '''
    __tablename__ = 'security_right'
    __table_args__ = (UniqueConstraint('fk_right_type_id', 'name', name='uix_type_name'),
                      dict(mysql_engine='InnoDB', mysql_charset='utf8'))

    Id = Column('id', INTEGER(unsigned=True), primary_key=True)
    Type = relationshipModel(RightTypeMapped.id)
    Name = Column('name', String(150), nullable=False)
    Description = Column('description', String(255))

class RightAccess(Base, WithAclAccess):
    '''
    Provides the Right to Access mapping.
    '''
    __tablename__ = 'acl_right_access'
    
    aclId = Column('fk_right_id', ForeignKey(RightMapped.Id, ondelete='CASCADE'))
    
class RightCompensate(Base, WithCompensate):
    '''
    Provides the Right to Compensate mapping.
    '''
    __tablename__ = 'acl_right_compensate'
    
    aclAccessId = Column('fk_right_access_id', ForeignKey(RightAccess.id, ondelete='CASCADE'))