'''
Created on Aug 22, 2013

@package: gui core
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

XML Digester rules.
'''

from ally.design.processor.attribute import attribute, defines
from ally.design.processor.context import Context
from ally.design.processor.resolvers import merge
from ally.support.util_context import IPrepare
from ally.xml.digester import Rule, Digester
from ally.xml.context import DigesterArg
from ally.core.error import DevelError

# --------------------------------------------------------------------

class WithTracking(Context):
    '''
    Context class with tracking info.
    '''
    lineNumber = attribute(int, doc='''
    @rtype: int
    The starting line number for this element in the configuration file. 
    ''')
    colNumber = attribute(int, doc='''
    @rtype: int
    The starting column number for this element in the configuration file. 
    ''')
    uri = attribute(str, doc='''
    @rtype: str
    Uri of the file containing this element. 
    ''')

def trackOn(digester, context):
    '''
    Will set the tracking attributes on context
    '''
    assert isinstance(digester, Digester), 'Invalid digester %s' % digester
    assert isinstance(context, WithTracking), 'Invalid context %s' % context
    
    context.lineNumber, context.colNumber, context.uri = digester.getLineNumber(), digester.getColumnNumber(), digester.arg.solicit.uri

# --------------------------------------------------------------------

class GroupRule(Rule, IPrepare):
    '''
    Digester rule for extracting groups from the xml configuration file.
    '''
    
    class Repository(WithTracking):
        '''
        The group context.
        '''
        # ---------------------------------------------------------------- Defined
        groupName = defines(str, doc='''
        @rtype: string
        The name of the group (e.g. "Anonymous").
        ''')
        description = defines(str, doc='''
        @rtype: string
        The description of the group (e.g. "Allows for the viewing of all possible requests").
        ''')
        children = defines(list, doc='''
        @rtype: list[Context]
        The list of children created.
        ''')
    
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Repository=self.Repository))
        
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        
        group = digester.arg.Repository()
        assert isinstance(group, GroupRule.Repository)        
        group.groupName = digester.currentName()
        trackOn(digester, group)
        digester.stack.append(group)
        
    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected a repository on the digester stack'
        group = digester.stack.pop()
        assert isinstance(group, self.Repository), 'Invalid repository %s' % group        
        repository = digester.stack[-1]
        assert isinstance(repository, self.Repository), 'Invalid repository %s' % repository
        
        if repository.children is None: repository.children = []
        repository.children.append(group)

class RightRule(GroupRule):
    '''
    Digester rule for extracting rights from the xml configuration file.
    '''
    class Repository(WithTracking):
        '''
        The right context.
        '''
        # ---------------------------------------------------------------- Defined
        rightName = defines(str, doc='''
        @rtype: string
        The name of the right.
        ''')
        rightInherits = defines(list, doc='''
        @rtype: string
        The list of name of inherited rights.
        ''')
        description = defines(str, doc='''
        @rtype: string
        The description of the group (e.g. "Allows for the viewing of all possible requests").
        ''')
        children = defines(list, doc='''
        @rtype: list[Context]
        The list of children created.
        ''')
    
    def __init__(self, name, inherits):
        '''
        @param name: the configuration attribute containing the name of the right
        @param parent: the configuration attribute containing the name of the parent right
        ''' 
        self.name = name
        self.inherits = inherits
        
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        repository = digester.arg.Repository()
        assert isinstance(repository, RightRule.Repository), 'Invalid repository %s' % repository
        repository.rightName = attributes.get(self.name)
        if attributes.get(self.inherits): repository.rightInherits = attributes.get(self.inherits).split(',')
        trackOn(digester, repository)
        digester.stack.append(repository)

class ActionRule(Rule, IPrepare):
    '''
    Digester rule for extracting actions from the xml configuration file.
    '''
    
    class Repository(Context):
        '''
        The repository context.
        '''
        # ---------------------------------------------------------------- Defined
        parent = attribute(Context, doc='''
        @rtype: Context
        The parent context for repository. 
        ''')
        actions = defines(list, doc='''
        @rtype: list[Context]
        The list of actions created.
        ''')
        
    class Action(WithTracking):
        '''
        The action container context.
        '''
        # ---------------------------------------------------------------- Defined
        path = defines(str, doc='''
        @rtype: string
        The action path.
        ''')
        label = defines(str, doc='''
        @rtype: string
        The action label.
        ''')
        script = defines(str, doc='''
        @rtype: string
        The action java script file path.
        ''')
        navBar = defines(str, doc='''
        @rtype: string
        The navigation bar update path.
        ''')
    
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Repository=ActionRule.Repository, Action=ActionRule.Action))
    
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert issubclass(digester.arg.Repository, ActionRule.Repository), \
        'Invalid repository class %s' % digester.arg.Repository
        assert issubclass(digester.arg.Action, ActionRule.Action), \
        'Invalid repository class %s' % digester.arg.Repository
        
        assert digester.stack, 'Expected a repository on the digester stack'
        repository = digester.stack[-1]
        assert isinstance(repository, ActionRule.Repository), 'Invalid repository %s' % repository
        
        if 'path' not in attributes:
            raise DevelError('A path attribute is required at line %s and column for \'%s\'' % 
                             (digester.getLineNumber(), digester.getColumnNumber(), digester.currentName()))
        
        action = digester.arg.Action()
        assert isinstance(action, ActionRule.Action), 'Invalid action %s' % action
        action.path, action.label = attributes['path'], attributes.get('label')
        action.script, action.navBar = attributes.get('script'), attributes.get('navbar')
        if 'parent' in attributes: action.path = '%s.%s' % (attributes['parent'], action.path)
        
        trackOn(digester, action)
        
        if repository.actions is None: repository.actions = []
        repository.actions.append(action)
        
        digester.stack.append(digester.arg.Repository(parent=action))
        
    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        arepository = digester.stack.pop()
        # the parent repository - will move all actions from arepository to parent repository
        prepository = digester.stack[-1]
        
        assert isinstance(arepository, ActionRule.Repository), 'Invalid repository %s' % arepository
        assert isinstance(arepository.parent, ActionRule.Action), \
        'Invalid repository parent %s' % arepository.parent
        if arepository.actions:
            for child in arepository.actions:
                assert isinstance(child, ActionRule.Action), 'Invalid action %s' % child
                if not child.path.startswith(arepository.parent.path):
                    child.path = '%s.%s' % (arepository.parent.path, child.path)
                prepository.actions.append(child)


class AccessRule(Rule, IPrepare):
    '''
    Digester rule for extracting Access nodes from the xml configuration file.
    '''
    
    class Repository(Context):
        '''
        The repository context.
        '''
        # ---------------------------------------------------------------- Defined
        accesses = defines(list, doc='''
        @rtype: list[Context]
        ''')
    
    class Access(WithTracking):
        '''
        The access context.
        '''
        # ---------------------------------------------------------------- Defined
        filters = defines(list, doc='''
        @rtype: list[str]
        The list of filters.
        ''')
        
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Repository=AccessRule.Repository, Access=AccessRule.Access))
    
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected a repository on the digester stack'
        repository = digester.stack[-1]
        assert isinstance(repository, AccessRule.Repository), 'Invalid repository %s' % repository
        
        access = digester.arg.Access()
        if not access.filters: access.filters = []
        access.filters.extend([f.strip() for f in attributes.get('filter', '').split(',') if f])
        
        trackOn(digester, access)
        
        if repository.accesses is None: repository.accesses = []
        repository.accesses.append(access)
        digester.stack.append(access)
        
    def end(self, node, digester):
        '''
        @see: Rule.end
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Invalid stack %s' % digester.stack
        digester.stack.pop()
        
class URLRule(Rule, IPrepare):
    '''
    Digester rule for extracting URLs from the xml configuration file.
    '''
    
    class Access(Context):
        '''
        The access context.
        '''
        # ---------------------------------------------------------------- Defined
        urls = defines(list, doc='''
        @rtype: list[Context]
        The list of urls.
        ''')
        
    class URL(Context):
        '''
        The url context.
        '''
        # ---------------------------------------------------------------- Defined
        url = defines(str, doc='''
        @rtype: string
        The actual URL.
        ''')
        compensates = defines(list, doc='''
        @rtype: list[string]
        The list of URLs to compensate (can be None).
        ''')
    
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Access=URLRule.Access, URL=URLRule.URL))
    
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected access repository on the digester stack'
        access = digester.stack[-1]
        assert isinstance(access, URLRule.Access), 'Invalid Access class %s' % access
        
        #create the url here and add it to the access (also add the compensates to the url)
        if access.urls is None: access.urls = []
        url = digester.arg.URL()
        if attributes.get('alter'): 
            url.compensates = attributes.get('alter').split(',')
        access.urls.append(url)
        
    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected access repository on the digester stack'
        access = digester.stack[-1]
        assert isinstance(access, URLRule.Access), 'Invalid Access class %s' % access
        
        content = content.strip()
        if content:
            #update the last url on the access
            if access.urls: 
                url = access.urls[-1]
                assert isinstance(url, URLRule.URL), 'Invalid url context %s' % url
                url.url = content
        #else remove last url from access
        elif access.urls: access.urls.pop()
            
class MethodRule(Rule, IPrepare):
    '''
    Digester rule for extracting Methods from the xml configuration file.
    '''
    
    class Access(Context):
        '''
        The access context.
        '''
        # ---------------------------------------------------------------- Defined
        methods = defines(list, doc='''
        @rtype: list[str]
        The list of methods.
        ''')
    
    def __init__(self, fromAttributes=False):
        '''
        Construct the method rule
        
        @param fromAttributes: boolean
            The flag tells whether to parse methods from xml tags or xml attributes.
        '''
        assert isinstance(fromAttributes, bool), 'Invalid flag %s' % fromAttributes
        self.fromAttributes = fromAttributes
    
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Access=MethodRule.Access))
    
    def begin(self, digester, **attributes):
        '''
        @see: Rule.begin
        '''
        if not self.fromAttributes: return
        
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected a repository on the digester stack'
        access = digester.stack[-1]
        assert isinstance(access, MethodRule.Access), 'Invalid access class %s' % access
        
        if not access.methods: access.methods = []
        access.methods.extend([m.strip() for m in attributes.get('methods', '').split(',') if m])
        
    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        if self.fromAttributes: return
        
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected a repository on the digester stack'
        access = digester.stack[-1]
        assert isinstance(access, MethodRule.Access), 'Invalid access class %s' % access
        
        content = content.strip()
        if content:
            if access.methods is None: access.methods = []
            access.methods.append(content)
            
class DescriptionRule(Rule, IPrepare):
    '''
    Digester rule for extracting the description of a group.
    '''
    class Repository(Context):
        '''
        The repository context.
        '''
        # ---------------------------------------------------------------- Defined
        description = defines(str, doc='''
        @rtype: String
        The description of the group (e.g. "Allows for the viewing of all possible requests").
        ''')
     
    def prepare(self, resolvers):
        '''
        @see: IVerifier.prepare
        '''
        merge(resolvers, dict(Repository=DescriptionRule.Repository))
    
    def content(self, digester, content):
        '''
        @see: Rule.content
        '''
        assert isinstance(digester, DigesterArg), 'Invalid digester %s' % digester
        assert digester.stack, 'Expected a group repository on the digester stack'
        repository = digester.stack[-1]
        assert isinstance(repository, DescriptionRule.Repository), 'Invalid Repository class %s' % repository
        
        content = content.strip()
        if content:
            if repository.description is None: repository.description = ''
            repository.description += content
