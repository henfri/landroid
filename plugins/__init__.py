#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      <AUTHOR>                                  <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.5 and
#  upwards.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from lib.model.smartplugin import *
from lib.item import Items

from .webif import WebInterface
import sys

from _operator import or_
sys.path.append('/devtools/eclipse/plugins/org.python.pydev.core_8.1.0.202012051215/pysrc')
#sys.path.append('/home/smarthome/.p2/pool/plugins/org.python.pydev.core_6.5.0.201809011628/pysrc')
import pydevd

#pydevd.settrace("192.168.178.37", port=5678)
import asyncio
import pyworxcloud


# If a needed package is imported, which might be not installed in the Python environment,
# add it to a requirements.txt file within the plugin's directory



class landroid(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """

    PLUGIN_VERSION = '1.7.1'    # (must match the version specified in plugin.yaml), use '1.0.0' for your initial plugin Release

    def __init__(self, sh):
        """
        Initalizes the plugin.

        If you need the sh object at all, use the method self.get_sh() to get it. There should be almost no need for
        a reference to the sh object any more.

        Plugins have to use the new way of getting parameter values:
        use the SmartPlugin method get_parameter_value(parameter_name). Anywhere within the Plugin you can get
        the configured (and checked) value for a parameter by calling self.get_parameter_value(parameter_name). It
        returns the value in the datatype that is defined in the metadata.
        """

        # Call init code of parent class (SmartPlugin)
        self.logger = logging.getLogger(__name__)
        self.sh = self.get_sh()
        self.items = Items.get_instance()
        self.auth = False
        super().__init__()
        pydevd.settrace("192.168.178.37", port=5678)
        self.parent_item = self.get_parameter_value('parent_item')
        
        self.user = self.get_parameter_value('landroid_user')
        self.pwd = self.get_parameter_value('landroid_pwd')
        
        self.worx = pyworxcloud.WorxCloud()
        
        
        # Variante ohne asyncio - self.auth wird aber nicht richtig gesetzt
        #self.auth = self.worx._authenticate("hendrik@friedels.name","MeinWorx321!",'worx') 

        # get the parameters for the plugin (as defined in metadata plugin.yaml):
        # cycle time in seconds, only needed, if hardware/interface needs to be
        # polled for value changes by adding a scheduler entry in the run method of this plugin
        # (maybe you want to make it a plugin parameter?)
        self.cycle = self.get_parameter_value('cycle')

        # Initialization code goes here

        # On initialization error use:
        #   self._init_complete = False
        #   return

        # if plugin should start even without web interface
        self.init_webinterface(WebInterface)
        # if plugin should not start without web interface
        # if not self.init_webinterface():
        #     self._init_complete = False

        return

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.debug("Run method called")
        # setup scheduler for device poll loop   (disable the following line, if you don't need to poll the device. Rember to comment the self_cycle statement in __init__ as well)
        pydevd.settrace("192.168.178.37", port=5678)
        self.scheduler_add('poll_device', self.poll_device, cycle=self.cycle)

        self.alive = True
        self.worx_init()
        if self.auth == False:
            self.logger.warning("Cound not login to IOT @ Amazon - plugin is not working")
        # get the Values from Worx first Time
        self.poll_device()
        
        
        # New scheduler for next login - experitation = 31536000 Seconds = 365 Tage
        # Muss man wahrscheinlich bei 365 Tagen nicht haben
        # self.scheduler_add('worx_login', self.worx_init, cycle=31536000)


        # if you need to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        """
        Stop method for the plugin
        """
        # Find all running tasks:
        try:
            if (self.loop.is_running()):
                self.loop.close()
        except:
            pass
        
        self.logger.debug("Stop method called")
        self.scheduler_remove('poll_device')
        #self.scheduler_remove('worx_login')
        self.alive = False
    
    def worx_init(self):
        #pydevd.settrace("192.168.178.37", port=5678)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_until_complete(self.logon())
        try:
            self.loop.close()
        except:
            pass
        self.worx.connect(0, False)
        
    
    async def logon(self):
        # Initialize connection, using your worx email and password
        #auth = await worx.initialize("hendrik@friedels.name","MeinWorx321!") #worx.initialize("hendrik@friedels.name","MeinWorx321!")
        self.auth = await self.worx.initialize(self.user,self.pwd)

        if not self.auth:
            #If invalid credentials are used, or something happend during
            #authorize, then exit
            return False
        else:
            return True

        #asyncio.get_event_loop().run_until_complete(self.logon())
    
    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference
        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.
        """
        if self.has_iattr(item.conf, 'foo_itemtag'):
            self.logger.debug("parse item: {}".format(item))

        # todo
        # if interesting item for sending values:
        #   return self.update_item

    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Item has been updated

        This method is called, if the value of an item has been updated by SmartHomeNG.
        It should write the changed value out to the device (hardware/interface) that
        is managed by this plugin.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        if self.alive and caller != self.get_shortname():
            # code to execute if the plugin is not stopped
            # and only, if the item has not been changed by this this plugin:
            self.logger.info("Update item: {}, item has been changed outside this plugin".format(item.id()))

            if self.has_iattr(item.conf, 'foo_itemtag'):
                self.logger.debug("update_item was called with item '{}' from caller '{}', source '{}' and dest '{}'".format(item,
                                                                                                               caller, source, dest))
            pass

    def poll_device(self):
        """
        Polls for updates of the device

        This method is only needed, if the device (hardware/interface) does not propagate
        changes on it's own, but has to be polled to get the actual status.
        It is called by the scheduler which is set within run() method.
        """
        # # get the value from the device
        # device_value = ...
        #
        # # find the item(s) to update:
        # for item in self.sh.find_items('...'):
        #
        #     # update the item by calling item(value, caller, source=None, dest=None)
        #     # - value and caller must be specified, source and dest are optional
        #     #
        #     # The simple case:
        #     item(device_value, self.get_shortname())
        #     # if the plugin is a gateway plugin which may receive updates from several external sources,
        #     # the source should be included when updating the the value:
        #     item(device_value, self.get_shortname(), source=device_source_id)
        
        
        if self.auth:
            #Force and update request to get latest state from the device
            self.worx.update()
            
            #Read latest states received from the device
            self.worx.getStatus()
        
            #Store all attributes received from the device to items
            #pydevd.settrace("192.168.178.37", port=5678)
            attrs = vars(self.worx)
            for item in attrs:
                self.logger.warning("Got item {} with value {}".format(item,attrs[item]))
                try:
                    self._set_childitem(item, attrs[item])
                except:
                    pass

    ##############################################
    # Private functions
    ##############################################
    def _get_childitem(self, itemname):
        """
        a shortcut function to get value of an item if it exists
        :param itemname:
        :return:
        """
        item = self.items.return_item(self.parent_item + '.' + itemname)  
        if (item != None):
            return item()
        else:
            self.logger.warning("Could not get item '{}'".format(self.parent_item+'.'+itemname))    
    
    
    def _set_childitem(self, itemname, value ):
        """
        a shortcut function to set an item with a given value if it exists
        :param itemname:
        :param value:
        :return:
        """
        item = self.items.return_item(self.parent_item + '.' + itemname)  
        if (item != None): 
            item(value, self.get_shortname())
        else:
            self.logger.warning("Could not set item '{}' to '{}'".format(self.parent_item+'.'+itemname, value))
