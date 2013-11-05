'''
Created on Jan 17, 2012

@package: support sqlalchemy
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the database settings for the application database.
'''

from ally.container import ioc, support
from ally.design.processor.assembly import Assembly
from ally.design.processor.handler import Handler
from sql_alchemy import database_config
from sql_alchemy.core.impl.binder import BinderHandler
from sql_alchemy.core.impl.processor.binder.error_translator import \
    ErrorTranslatorHandler
from sql_alchemy.core.impl.processor.binder.session import BindSessionHandler
from sql_alchemy.database_config import alchemySessionCreator, metas


# --------------------------------------------------------------------
support.include(database_config)

# --------------------------------------------------------------------

alchemySessionCreator = alchemySessionCreator
metas = metas

@ioc.replace(database_url)
def database_url():
    '''This database URL is used for the application tables'''
    return 'sqlite:///workspace/shared/application.db'

# --------------------------------------------------------------------

@ioc.entity
def assemblyBind() -> Assembly:
    '''The assembly containing the handlers used for binding services/classes with SQL alchemy support'''
    return Assembly('Bind SQL alchemy')

@ioc.entity
def assemblySQLAssembler() -> Assembly:
    '''
    The assembly containing the handlers to be used in the assembly of invokers for error handling.
    '''
    return Assembly('Assemblers SQL alchemy', reportUnused=False)

# --------------------------------------------------------------------

@ioc.entity
def binder():
    b = BinderHandler()
    b.bindAssembly = assemblyBind()
    return b

@ioc.entity
def bindSession() -> Handler:
    b = BindSessionHandler()
    b.sessionCreator = alchemySessionCreator()
    return b

@ioc.entity
def errorTranslator() -> Handler:
    b = ErrorTranslatorHandler()
    b.assembly = assemblySQLAssembler()
    return b

# --------------------------------------------------------------------

@ioc.before(assemblyBind)
def updateAssemblyBind():
    assemblyBind().add(bindSession(), errorTranslator())
    
# --------------------------------------------------------------------

def bindApplicationSession(proxy):
    binder().bind(proxy)
