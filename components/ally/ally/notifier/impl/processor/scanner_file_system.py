'''
Created on Sep 13, 2013

@author: mihaigociu

@package: ally base
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Mihai Gociu

Scanning the items tree.
'''

from collections import deque
import logging
import os
from threading import Thread
from time import sleep
from ally.container.ioc import injected
from ally.design.processor.attribute import attribute, requires
from ally.design.processor.context import Context
from ally.design.processor.handler import HandlerProcessor
from ally.support.util_spec import IDo


# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

class Register(Context):
    '''
    The register context.
    '''
    # ---------------------------------------------------------------- Defines
    itemTree = attribute(Context, doc='''
    @rtype: Context
    The root of the item tree structure
    ''')
    # ---------------------------------------------------------------- Requires
    listeners = requires(list)    

class ItemFile(Context):
    '''
    The file system item context.
    '''
    # ---------------------------------------------------------------- Defined
    parent = attribute(Context, doc='''
    @rtype: Context
    The parent item.
    ''')
    name = attribute(str, doc='''
    @rtype: string
    The item name.
    ''')
    path = attribute(str, doc='''
    @rtype: string
    The path of the item.
    ''')
    uri = attribute(str, doc='''
    @rtype: string
    The path of the item.
    ''')
    lastModified = attribute(int, doc='''
    @rtype: integer
    The time of the modification.
    ''')
    children = attribute(dict, doc='''
    @rtype: dictionary{string: Context}
    The children items.
    ''')
    listeners = attribute(list, doc='''
    @rtype: list[Context]
    The list of listeners for this item.
    ''')
        
class Listener(Context):
    '''
    The file system item context.
    '''
    #---------------------------------------------------Defined
    path = attribute(str, doc='''
    @rtype: string
    The file system path of the listener.
    ''')
    #----------------------------------------------------Requires
    uri = requires(str)
    doMatch = requires(IDo)
    doMatchResource = requires(IDo)
    doOnContentCreated = requires(IDo)
    doOnContentChanged = requires(IDo)
    doOnContentRemoved = requires(IDo)
    
# --------------------------------------------------------------------

@injected
class FileSystemScanner(HandlerProcessor):
    '''
    Scans the item tree for modified items.
    '''
    
    def __init__(self):
        super().__init__(Listener=Listener)
    
    def process(self, chain, register:Register, Item:ItemFile, **keyargs):
        '''
        @see: HandlerProcessor.process
        
        First creates the items tree and adds the listeners.
        Then it scans the items tree and launches notifications.
        '''
        assert isinstance(register, Register), 'Invalid register %s' % register
        if not register.listeners: return
        
        if not register.itemTree: register.itemTree = self.createItem(None, None, Item)
        if not register.itemTree.children: register.itemTree.children = dict()
        
        listeners = []
        for listener in register.listeners:
            assert isinstance(listener, Listener), 'Invalid listener %s' % listener
            assert isinstance(listener.uri, str), 'Invalid uri %s' % listener.uri
            
            if listener.uri.startswith('file://'):
                listener.path = listener.uri[len('file://'):].replace('/', os.path.sep)
                listeners.append(listener)
        
        if not listeners: return
        self.createItemTree(listeners, register.itemTree, Item)
        
        scanThread = ScannerThread(target=self.scanItems, name='File system notifier scanner thread',
                                   args=(register.itemTree, Item))
        scanThread.daemon = True
        scanThread.start()
    
    def createItemTree(self, listeners, root, Item):
        '''
        Creates a tree structure of items that match the patterns of the listeners.
        '''
        assert isinstance(listeners, list), 'Invalid listeners %s' % listeners 
        
        for listener in listeners:
            assert isinstance(listener, Listener), 'Invalid listener %s' % listener
            assert listener.path, 'Invalid listener path %s' % listener.path
            
            offset = 0
            if os.path.isabs(listener.path): offset = 1
            startName = listener.path[:listener.path.find(os.path.sep, offset)]
            if not os.path.isdir(startName) and not os.path.isfile(startName) : continue
             
            queue = deque()
            queue.append((startName, root))  # name, parent
            while queue:
                name, parent = queue.popleft()
                assert isinstance(name, str), 'Invalid item name %s' % name
                assert isinstance(parent, ItemFile), 'Invalid item parent %s' % parent
                
                item = parent.children.get(name)
                if item is None:
                    path = os.path.join(parent.path or '', name)
                    #match with listener
                    if os.path.isfile(path):
                        if not listener.doMatchResource('file://%s' % '/'.join(path.split(os.path.sep))): continue
                    elif not listener.doMatch('file://%s' % '/'.join(path.split(os.path.sep))): continue
                    
                    # if the item does not exist, create it and add it to the tree
                    item = self.createItem(name, path, Item, parent)
                    assert isinstance(item, ItemFile), 'Invalid item %s' % item
                    # add the new item to the tree (by linking the parent to it)
                    if item.parent.children is None: item.parent.children = {} 
                    item.parent.children[item.name] = item
                    
                    # if the item is a file - notify listener
                    if os.path.isfile(item.path):
                        with open(item.path, 'rb') as content: listener.doOnContentCreated(item.uri, content)
                
                #match with listener
                if os.path.isfile(item.path):
                    if not listener.doMatchResource(item.uri): continue
                elif not listener.doMatch(item.uri): continue
                # add the listener
                item.listeners.append(listener)
                
                # get the children of this node and add them to the queue
                if os.path.isdir(item.path):
                    queue.extend((f, item) for f in os.listdir(item.path) if not f.startswith('.'))
        
        return root
    
    def scanItems(self, root, Item):
        '''
        Scans the items tree and keeps it updated. Also launches create, update, delete notifications for listeners.
        '''
        assert isinstance(root, ItemFile), 'Invalid item %s' % root
        
        # scan the tree
        queue = deque()
        queue.append(root)
        while queue:
            # get the node
            item = queue.pop()
            assert isinstance(item, ItemFile), 'Invalid item %s' % item
            
            if item.path is not None:
                # check that the path still exists; if not, delete it from the items tree
                if not os.path.exists(item.path):
                    item.parent.children.pop(item.name)
                    continue
            
                # compare the lastModified attribute on the item with the ... 
                lastModified = int(os.path.getmtime(item.path))
                if item.lastModified != lastModified:
                    assert log.debug('Item changed: %s' % item.path) or True
                    # recreate child items if item.path is a directory
                    if os.path.isdir(item.path): item = self.rebuildItems(item, Item)
                    # do something else if item.path is a file - like launch the file parser
                    elif os.path.isfile(item.path):
                        for listener in item.listeners:
                            assert isinstance(listener, Listener), 'Invalid listener %s' % listener
                            with open(item.path, 'rb') as content: listener.doOnContentChanged(item.uri, content)
                        
                    item.lastModified = lastModified
                
            if item.children: queue.extend(item.children.values())
    
    def rebuildItems(self, item, Item):
        '''
        The method is called when an item is modified. It will update the children of the item. 
        '''
        assert isinstance(item, ItemFile), 'Invalid item %s' % item
        
        # compare the list of known children with the list of newly read children
        currentChildren = set(item.children.keys())
        newChildren = set()
        path = item.path
        if os.path.isdir(path):
            for child in os.listdir(path):
                newChildren.add(child)
        
        # create the children that are missing; at the end
        for child in newChildren:
            if child in currentChildren: currentChildren.remove(child) 
            else:
                # create the child item and add it to the parent children list
                self.onCreateItem(item, child, Item)
        
        # delete the children that are no longer present on the disk
        assert isinstance(item.children, dict)
        for child in currentChildren:
            childItem = item.children.pop(child)
            self.onDeleteItem(childItem)
        
        return item
    
    def onCreateItem(self, item, childName, Item):
        '''
        Recursively creates the subtree starting with childName for the given item, and launches on_content_created notifications on the way.
        '''
        assert isinstance(item, ItemFile), 'Invalid item %s' % item
        assert isinstance(childName, str), 'Invalid item name %s' % childName
        # create the child item and add it to the parent children list
        queue = deque()
        queue.append((childName, item))
        
        while queue:
            childName, parent = queue.popleft()
            childPath = os.path.join(parent.path, childName)
            childUri = 'file://%s' % '/'.join(childPath.split(os.path.sep))
            
            listeners = []
            for listener in parent.listeners:
                assert isinstance(listener, Listener), 'Invalid listener %s' % listener
                #match with listener
                if os.path.isfile(childPath):
                    if listener.doMatchResource(childUri): listeners.append(listener)
                elif listener.doMatch(childUri): listeners.append(listener)
        
            if not listeners: continue
                
            childItem = self.createItem(childName, childPath, Item, parent)
            childItem.listeners = listeners
            # add the child item to its parent
            parent.children[childItem.name] = childItem
            
            # if the child is a file, send on_created notification
            if os.path.isfile(childItem.path):
                for listener in childItem.listeners:
                    with open(childItem.path, 'rb') as content: listener.doOnContentCreated(childItem.uri, content)
            # else if child is a directory, add its children to the queue
            elif os.path.isdir(childItem.path):
                for child in os.listdir(childItem.path):
                    queue.append((child, childItem))
        return item
            
    def onDeleteItem(self, item):
        '''
        Recursively launches do_on_delete events for the given item and all of its children.
        '''
        assert isinstance(item, ItemFile), 'Invalid item %s' % item
        
        queue = deque()
        queue.append(item)
        while queue:
            item = queue.popleft()
            # if child is file, launch do_on_content_removed for each listener
            for listener in item.listeners:
                assert isinstance(listener, Listener), 'Invalid listener %s' % listener
                listener.doOnContentRemoved(item.uri)
            
            if item.children: queue.extend(item.children.values())

    def createItem(self, name, path, Item, parent=None):
        item = Item()
        assert isinstance(item, ItemFile), 'Invalid item %s' % item
        item.name = name
        item.path = path
        item.parent = parent
        item.listeners = []
        item.children = dict()
        
        # only set lastModified time-stamp for non ROOT items
        if path:
            item.uri = 'file://%s' % '/'.join(path.split(os.path.sep))
            item.lastModified = int(os.path.getmtime(path))
            
        return item

class ScannerThread(Thread):
    def run(self):
        while True:
            if self._target:
                self._target(*self._args, **self._kwargs)
            sleep(1)
    
