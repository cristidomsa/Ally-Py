'''
Created on Aug 22, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Parses XML files based on digester rules.
'''

from ally.container.ioc import injected
from ally.design.processor.attribute import requires, defines
from ally.design.processor.context import Context
from ally.design.processor.execution import Chain
from ally.design.processor.handler import HandlerProcessor
from ally.xml.context import DigesterArg, prepare
from ally.xml.digester import Node
import logging
from ally.support.util_io import IInputStream

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Solicit(Context):
    '''
    The solicit context.
    '''
    # ---------------------------------------------------------------- Defined
    repository = defines(Context, doc='''
    @rtype: Context
    The parsed repository.
    ''')
    # ---------------------------------------------------------------- Required
    stream = requires(IInputStream)
    uri = requires(str)

# --------------------------------------------------------------------

@injected
class ParserHandler(HandlerProcessor):
    '''
    Implementation for a processor that parses XML files based on digester rules.
    '''
    
    # The root node to use for parsing.
    rootNode = Node
    
    def __init__(self):
        assert isinstance(self.rootNode, Node), 'Invalid node %s' % self.rootNode
        super().__init__(**prepare(self.rootNode))
        
        #used for mapping each repository to a URI
        self.uriRepository = dict()
        self._inError = False

    def process(self, chain, solicit:Solicit, Repository:Context, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        Parse the solicited files.
        '''
        assert isinstance(chain, Chain), 'Invalid chain %s' % chain
        assert isinstance(solicit, Solicit), 'Invalid solicit %s' % solicit
        
        #if there is no stream, just clean the repository for this URI (delete URI from self.uriRepository)
        if solicit.stream is None: self.uriRepository.pop(solicit.uri, None)
        else:
            digester = DigesterArg(chain.arg, self.rootNode, acceptUnknownTags=False)
            digester.stack.append(Repository())
            try:
                digester.parse('utf8', solicit.stream)
                if self._inError: log.warning('XML parsing OK')
                self._inError = False
            except Exception as e:
                if not self._inError: log.error(e)
                self._inError = True
                chain.cancel()
                return
            self.uriRepository[solicit.uri] = digester.stack.pop()
        
        #will make a root repository that contains all the repositories created so far (from the parsed files)
        root = chain.arg.Repository()
        root.children = []
        for repository in self.uriRepository.values():
            root.children.append(repository)
        
        solicit.repository = root
        