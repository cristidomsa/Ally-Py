'''
Created on Oct 9, 2013

@package: gateway
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Special module that is used in application deploy that provides the full IPs access management.
'''

import logging

from __setup__.ally.deploy import FLAG_START
from ally.container import deploy
from ally.container.support import entityFor
from application import parser, options
from gateway.api.gateway import IGatewayService, Custom


# --------------------------------------------------------------------
log = logging.getLogger(__name__)

FLAG_FULL_IP = 'fullIP'
# Flag indicating the management of full access IPs.

# --------------------------------------------------------------------

@deploy.prepare
def prepareGatewayActions():
    
    options.addIPs = None
    options.remIPs = None
    
    options.registerFlag(FLAG_FULL_IP, FLAG_START)
    options.registerFlagLink('addIPs', FLAG_FULL_IP)
    options.registerFlagLink('remIPs', FLAG_FULL_IP)
    
    parser.add_argument('-add-access', metavar='IP', dest='addIPs', nargs='+',
                        help='Provide this option to add a full access IPs, all calls from this IP will not be '
                        'blocked by the gateway, the IPs can be provided as: 127.0.0.1 or 127.*.*.*')
    parser.add_argument('-rem-access', metavar='IP', dest='remIPs', nargs='+',
                        help='Provide this option to remove full access IPs, the IPs need to be provided exactly '
                        'with the same form (127.0.0.1 or 127.*.*.*) as they have been added')

# --------------------------------------------------------------------

@deploy.start
def fullAccessIPs():
    if not options.isFlag(FLAG_FULL_IP): return
    
    serviceGateway = entityFor(IGatewayService)
    assert isinstance(serviceGateway, IGatewayService)
    
    if options.addIPs:
        for ip in options.addIPs:
            gateway = Custom()
            gateway.Name = 'full_access_%s' % ip
            gateway.Clients = ['\.'.join(mark.replace('*', '\d+') for mark in ip.split('.'))]
            try: serviceGateway.insert(gateway)
            except: log.info('IP \'%s\' already present', ip)
            else: log.info('IP \'%s\' added', ip)
            
    if options.remIPs:
        for ip in options.remIPs:
            if serviceGateway.delete('full_access_%s' % ip): log.info('IP \'%s\' removed', ip)
            else: log.info('IP \'%s\' is not present', ip)
