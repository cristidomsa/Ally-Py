'''
Created on Nov 14, 2012

@package: gateway acl
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the decorator to be used by the models in the ACL domain.
'''

from ally.api.config import model
from functools import partial

# --------------------------------------------------------------------

DOMAIN = 'ACL/'
modelACL = partial(model, domain=DOMAIN)
