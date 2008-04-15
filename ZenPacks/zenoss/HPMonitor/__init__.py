###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2008, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import Globals
import os.path

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

from Products.ZenModel.ZenPack import ZenPackBase

class ZenPack(ZenPackBase):
    """ HPMonitor loader
    """

    def install(self, app):
        ZenPackBase.install(self, app)
        self.setupCollectorPlugins(app.zport.dmd)

    def upgrade(self, app):
        ZenPackBase.upgrade(self, app)
        self.setupCollectorPlugins(app.zport.dmd)

    def remove(self, app, leaveObjects=False):
        self.cleanupOurPlugins(app.zport.dmd)
        ZenPackBase.remove(self, app, leaveObjects)

    def setupCollectorPlugins(self, dmd):
        self.cleanupOldPlugins(dmd)

        def addHPPlugins(obj):
            if obj.hasProperty('zCollectorPlugins'):
                newPlugins = []
                for plugin in obj.zCollectorPlugins:
                    newPlugins.append(plugin)
                    if plugin == 'zenoss.snmp.DeviceMap':
                        newPlugins.append('HPDeviceMap')
                    elif plugin == 'zenoss.snmp.CpuMap':
                        newPlugins.append('HPCPUMap')
                obj.zCollectorPlugins = newPlugins

        if hasattr(dmd.Devices, 'Server'):
            addHPPlugins(dmd.Devices.Server)
            if hasattr(dmd.Devices.Server, 'Linux'):
                addHPPlugins(dmd.Devices.Server.Linux)
            if hasattr(dmd.Devices.Server, 'Windows'):
                addHPPlugins(dmd.Devices.Server.Windows)

    def cleanupCollectorPlugins(self, dmd, plugin_list):
        obj_list = [dmd.Devices] + dmd.Devices.getSubOrganizers() + \
                dmd.Devices.getSubDevices()

        for thing in obj_list:
            if not thing.hasProperty('zCollectorPlugins'): continue
            newPlugins = []
            for plugin in thing.zCollectorPlugins:
                if plugin in plugin_list:
                    continue
                newPlugins.append(plugin)
            thing.zCollectorPlugins = newPlugins

    def cleanupOurPlugins(self, dmd):
        self.cleanupCollectorPlugins(dmd, ('HPDeviceMap', 'HPCPUMap'))

    def cleanupOldPlugins(self, dmd):
        self.cleanupCollectorPlugins(dmd, (
                'zenoss.snmp.HPDeviceMap', 'zenoss.snmp.HPCPUMap'))

