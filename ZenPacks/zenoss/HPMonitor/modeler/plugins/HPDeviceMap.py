###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

__doc__ = """HPDeviceMap
Use HP Insight Manager to determine hardware model + serial number as well
as OS information.
"""

from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetMap
from Products.DataCollector.plugins.DataMaps import MultiArgs
import re

class HPDeviceMap(SnmpPlugin):
    """Map mib elements from HP Insight Manager mib to get hw and os products.
    """

    maptype = "HPDeviceMap" 

    snmpGetMap = GetMap({ 
        '.1.3.6.1.4.1.232.2.2.2.1.0' : 'setHWSerialNumber',
        '.1.3.6.1.4.1.232.2.2.4.2.0' : 'setHWProductKey',
        '.1.3.6.1.4.1.232.11.2.2.1.0': 'setOSProductKey',
         })


    def process(self, device, results, log):
        """collect snmp information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        getdata, tabledata = results
        if getdata['setHWProductKey'] is None: return None
        om = self.objectMap(getdata)
        if om.setHWSerialNumber:
            om.setHWSerialNumber = om.setHWSerialNumber.strip()
        om.setHWProductKey = MultiArgs(om.setHWProductKey, "HP")

        if om.setOSProductKey and om.setOSProductKey.find("NetWare") > -1:
            delattr(om, 'setOSProductKey')
        else:
            if re.search(r'Microsoft', om.setOSProductKey, re.I):
                om.setOSProductKey = MultiArgs(om.setOSProductKey, "Microsoft")
            elif re.search(r'Red\s*Hat', om.setOSProductKey, re.I):
                om.setOSProductKey = MultiArgs(om.setOSProductKey, "RedHat")
        return om
