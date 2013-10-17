'''
Created on Oct 9, 2013

@package: ally plugin
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the logging configurations to be used for the application.
'''

import logging

import __plugin__
from ally.container import ioc, deploy
from ally.design import processor

from ..ally.deploy import PRIORITY_LOGGING
from ..ally.logging import info_for
from .distribution import application_mode, APP_DEVEL


# --------------------------------------------------------------------
@deploy.start(PRIORITY_LOGGING)
def loggingDevelopment():
    if application_mode() == APP_DEVEL:
        logging.getLogger(processor.__name__).setLevel(logging.INFO)

@ioc.before(info_for)
def updateInfos():
    info_for().append(__plugin__.__name__)
