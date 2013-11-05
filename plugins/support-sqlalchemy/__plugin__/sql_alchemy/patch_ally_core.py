'''
Created on Aug 30, 2013

@package: support sqlalchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations patch for the processors used in handling the request.
'''

import logging

from ally.container import ioc, app
from ally.design.processor.handler import Handler

from .db_application import assemblySQLAssembler
from sql_alchemy.core.impl.processor.assembler.mapped_validation import MappedValidationHandler


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_core  # @UnusedImport
except ImportError: log.info('No ally core component available, thus no need to apply the transaction patch')
else:
    from __setup__.ally_core.processor import invoking
    from __setup__.ally_core_http.processor import assemblyResources, updateAssemblyResources
    from __setup__.ally_core.resources import invokerService, processMethod
    from __setup__.ally_core.resources import assemblyAssembler, updateAssemblyAssembler, decoding
    from sql_alchemy.core.impl.processor import transaction_core
    
    @ioc.entity
    def transactionCore() -> Handler: return transaction_core.TransactionCoreHandler()
    
    @ioc.entity
    def mappedValidation() -> Handler: return MappedValidationHandler()

    # ----------------------------------------------------------------

    @ioc.after(updateAssemblyAssembler)
    def updateAssemblyAssemblerForMetaValidation():
        assemblyAssembler().add(mappedValidation(), before=decoding())
        
    @ioc.after(assemblySQLAssembler)
    def updateAssemblySQLAssembler():
        assemblySQLAssembler().add(invokerService(), processMethod())

    @ioc.after(updateAssemblyResources)
    def updateAssemblyResourcesForAlchemy():
        assemblyResources().add(transactionCore(), before=invoking())
    
    @app.deploy(app.DEVEL)
    def updateLoggingForSQLErrors():
        logging.getLogger(transaction_core.__name__).setLevel(logging.INFO)
