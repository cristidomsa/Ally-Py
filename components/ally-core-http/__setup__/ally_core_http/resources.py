'''
Created on Jun 1, 2012

@package: ally core http
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the configurations for the resources.
'''

from ..ally_core.resources import encoding, processMethod, \
    updateAssemblyAssembler, assemblyAssembler
from .decode import assemblyDecodeParameters
from ally.container import ioc
from ally.core.http.impl.processor.assembler.conflict_replace import \
    ConflictReplaceHandler
from ally.core.http.impl.processor.assembler.conflict_resolve import \
    ConflictResolveHandler
from ally.core.http.impl.processor.assembler.decoding_parameter import \
    DecodingParameterHandler
from ally.core.http.impl.processor.assembler.invoker_node import \
    InvokerNodeHandler
from ally.core.http.impl.processor.assembler.invoker_resources import \
    InvokerResourcesHandler
from ally.core.http.impl.processor.assembler.method_http import \
    MethodHTTPHandler
from ally.core.http.impl.processor.assembler.path_domain import \
    PathDomainHandler
from ally.core.http.impl.processor.assembler.path_for_update import \
    PathUpdateHandler
from ally.core.http.impl.processor.assembler.path_get_accessible import \
    PathGetAccesibleHandler
from ally.core.http.impl.processor.assembler.path_get_model import \
    PathGetModelHandler
from ally.core.http.impl.processor.assembler.path_on_input import \
    PathInputHandler
from ally.core.http.impl.processor.assembler.path_on_target import \
    PathTargetHandler
from ally.core.http.impl.processor.assembler.path_slash import PathSlashHandler
from ally.core.http.impl.processor.assembler.path_web_name import \
    PathWebNameHandler
from ally.core.http.impl.processor.scheme import AssemblerSchemeHandler
from ally.design.processor.handler import Handler

# --------------------------------------------------------------------

@ioc.entity
def decodingParameter() -> Handler:
    b = DecodingParameterHandler()
    b.decodeAssembly = assemblyDecodeParameters()
    return b

@ioc.entity
def methodHTTP() -> Handler: return MethodHTTPHandler()

@ioc.entity
def pathInput() -> Handler: return PathInputHandler()

@ioc.entity
def pathUpdate() -> Handler: return PathUpdateHandler()

@ioc.entity
def pathTarget() -> Handler: return PathTargetHandler()

@ioc.entity
def pathDomain() -> Handler: return PathDomainHandler()

@ioc.entity
def pathWebName() -> Handler: return PathWebNameHandler()

@ioc.entity
def invokerResources() -> Handler: return InvokerResourcesHandler()

@ioc.entity
def invokerNode() -> Handler: return InvokerNodeHandler()

@ioc.entity
def conflictReplace() -> Handler: return ConflictReplaceHandler()

@ioc.entity
def conflictResolve() -> Handler: return ConflictResolveHandler()

@ioc.entity
def pathSlash() -> Handler: return PathSlashHandler()

@ioc.entity
def pathGetModel() -> Handler: return PathGetModelHandler()

@ioc.entity
def pathGetAccesible() -> Handler: return PathGetAccesibleHandler()

@ioc.entity
def assemblerScheme() -> Handler: return AssemblerSchemeHandler()

# --------------------------------------------------------------------

@ioc.after(updateAssemblyAssembler)
def updateAssemblyAssemblerForHTTPCore():
    assemblyAssembler().add(decodingParameter(), methodHTTP(), pathInput(), pathUpdate(), pathTarget(),
                            pathDomain(), pathWebName(), invokerResources(), invokerNode(), conflictReplace(),
                            conflictResolve(), pathSlash(), pathGetModel(), pathGetAccesible(), after=processMethod())

    assemblyAssembler().add(assemblerScheme(), after=encoding())
