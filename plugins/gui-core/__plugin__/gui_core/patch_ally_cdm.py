'''
Created on Oct 30, 2013

@package: gui core
@copyright: 2013 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Rus Mugurel

Provides the UI files publish patch for the cdm.
'''

import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

try:
    from __setup__ import ally_cdm # @UnusedImport
except ImportError:
    log.info('No ally cdm component available, thus no need to publish UI path to CDM')
else:
    from __setup__.ally_cdm.processor import repository_paths
    from os.path import join, isdir
    from ally.container import ioc
    import os
    
    @ioc.before(repository_paths)
    def configureUIPath():
        uiDir = join(os.pardir, 'ui')
        if isdir(uiDir):
            repository_paths().append(uiDir)
