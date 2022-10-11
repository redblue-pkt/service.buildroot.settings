# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2018-present Team CoreELEC (https://coreelec.org)

import log
import modules
import oe

import os
import re
import glob
import xbmc
import xbmcgui
import oeWindows
import threading
import subprocess
import shutil

class hardware(modules.Module):

    ENABLED = False
    menu = {'8': {
        'name': 32004,
        'menuLoader': 'load_menu',
        'listTyp': 'list',
        'InfoText': 780,
        }}


    disk_idle_times = [
        {
            "name": "Disabled",
            "value": "0"
        },
        {
            "name": "5 Minutes",
            "value": "300"
        },
        {
            "name": "10 Minutes",
            "value": "600"
        },
        {
            "name": "20 Minutes",
            "value": "1200"
        },
        {
            "name": "30 Minutes",
            "value": "1800"
        },
        {
            "name": "1 Hour",
            "value": "3600"
        },
        {
            "name": "2 Hours",
            "value": "7200"
        },
        {
            "name": "5 Hours",
            "value": "18000"
        },
    ]

    @log.log_function()
    def __init__(self, oeMain):
        super().__init__()
        self.struct = {
                'fan': {
                    'order': 1,
                    'name': 32420,
                    'not_supported': [],
                    'settings': {
                        'fan_mode': {
                            'order': 1,
                            'name': 32421,
                            'InfoText': 781,
                            'value': 'off',
                            'action': 'initialize_fan',
                            'type': 'multivalue',
                            'values': ['off', 'auto', 'manual'],
                            },
                        'fan_level': {
                            'order': 2,
                            'name': 32422,
                            'InfoText': 782,
                            'value': '0',
                            'action': 'set_fan_level',
                            'type': 'multivalue',
                            'values': ['0','1','2','3'],
                            'parent': {
                                'entry': 'fan_mode',
                                'value': ['manual'],
                                },
                            },

                        },
                    },
              'performance': {
                    'order': 2,
                    'name': 32403,
                    'not_supported': [],
                    'settings': {
                        'cpu_governor': {
                            'order': 1,
                            'name': 32423,
                            'InfoText': 783,
                            'value': '',
                            'action': 'set_cpu_governor',
                            'type': 'multivalue',
                            'values': ['conservative', 'ondemand', 'userspace', 'powersave', 'performance', 'schedutil'],
                            },
                        },
                    },
                'hdd': {
                    'order': 3,
                    'name': 32404,
                    'not_supported': [],
                    'settings': {
                        'disk_park': {
                            'order': 1,
                            'name': 32424,
                            'InfoText': 794,
                            'value': '0',
                            'action': 'set_disk_park',
                            'type': 'bool',
                            },
                        'disk_park_time': {
                            'order': 2,
                            'name': 32425,
                            'InfoText': 795,
                            'value': '10',
                            'action': 'set_disk_park',
                            'type': 'text',
                            },
                        'disk_idle': {
                            'order': 3,
                            'name': 32426,
                            'InfoText': 796,
                            'value': '',
                            'action': 'set_disk_idle',
                            'type': 'multivalue',
                            'values': ['Disabled'],
                            },
                        },
                    },

                }

    @log.log_function()
    def start_service(self):
            self.load_values()
            if not 'hidden' in self.struct['fan']:
                self.initialize_fan()
            self.set_cpu_governor()
            self.set_disk_park()
            self.set_disk_idle()

    @log.log_function()
    def stop_service(self):
        if hasattr(self, 'update_thread'):
            self.update_thread.stop()

    @log.log_function()
    def do_init(self):
            self.load_values()

    @log.log_function()
    def exit(self):
        pass

    @log.log_function()
    def load_values(self):
            if not os.path.exists('/sys/class/fan'):
                self.struct['fan']['hidden'] = 'true'
            else:
                value = oe.read_setting('hardware', 'fan_mode')
                if not value is None:
                    self.struct['fan']['settings']['fan_mode']['value'] = value
                value = oe.read_setting('hardware', 'fan_level')
                if not value is None:
                    self.struct['fan']['settings']['fan_level']['value'] = value

            cpu_clusters = ["", "cpu0/"]
            for cluster in cpu_clusters:
                sys_device = '/sys/devices/system/cpu/' + cluster + 'cpufreq/'
                if not os.path.exists(sys_device):
                    continue

                if os.path.exists(sys_device + 'scaling_available_governors'):
                    available_gov = oe.load_file(sys_device + 'scaling_available_governors')
                    self.struct['performance']['settings']['cpu_governor']['values'] = available_gov.split()

                value = oe.read_setting('hardware', 'cpu_governor')
                if value is None:
                    value = oe.load_file(sys_device + 'scaling_governor')

                self.struct['performance']['settings']['cpu_governor']['value'] = value

            value = oe.read_setting('hardware', 'disk_park')
            if not value is None:
                self.struct['hdd']['settings']['disk_park']['value'] = value

            value = oe.read_setting('hardware', 'disk_park_time')
            if not value is None:
                self.struct['hdd']['settings']['disk_park_time']['value'] = value
            else:
                self.struct['hdd']['settings']['disk_park_time']['value'] = '10'

            value = oe.read_setting('hardware', 'disk_idle')
            if value is None or value == '':
                value = 'Disabled'

            disk_idle_times_names = []
            self.struct['hdd']['settings']['disk_idle']['value'] = 'Disabled'
            for disk_idle_time in self.disk_idle_times:
              disk_idle_times_names.append(disk_idle_time["name"])
              if disk_idle_time["name"] in value:
                self.struct['hdd']['settings']['disk_idle']['value'] = disk_idle_time["name"]

            self.struct['hdd']['settings']['disk_idle']['values'] = disk_idle_times_names

    @log.log_function()
    def initialize_fan(self, listItem=None):
            self.busy = 1
            if not listItem == None:
                self.set_value(listItem)
            if os.access('/sys/class/fan/enable', os.W_OK) and os.access('/sys/class/fan/mode', os.W_OK):
                if self.struct['fan']['settings']['fan_mode']['value'] == 'off':
                    fan_enable = open('/sys/class/fan/enable', 'w')
                    fan_enable.write('0')
                    fan_enable.close()
                if self.struct['fan']['settings']['fan_mode']['value'] == 'manual':
                    fan_enable = open('/sys/class/fan/enable', 'w')
                    fan_enable.write('1')
                    fan_enable.close()
                    fan_mode_ctl = open('/sys/class/fan/mode', 'w')
                    fan_mode_ctl.write('0')
                    fan_mode_ctl.close()
                    self.set_fan_level()
                if self.struct['fan']['settings']['fan_mode']['value'] == 'auto':
                    fan_enable = open('/sys/class/fan/enable', 'w')
                    fan_enable.write('1')
                    fan_enable.close()
                    fan_mode_ctl = open('/sys/class/fan/mode', 'w')
                    fan_mode_ctl.write('1')
                    fan_mode_ctl.close()
            self.busy = 0

    @log.log_function()
    def set_fan_level(self, listItem=None):
            self.busy = 1
            if not listItem == None:
                self.set_value(listItem)
            if os.access('/sys/class/fan/level', os.W_OK):
                if not self.struct['fan']['settings']['fan_level']['value'] is None and not self.struct['fan']['settings']['fan_level']['value'] == '':
                    fan_level_ctl = open('/sys/class/fan/level', 'w')
                    fan_level_ctl.write(self.struct['fan']['settings']['fan_level']['value'])
                    fan_level_ctl.close()
            self.busy = 0

    @log.log_function()
    def set_cpu_governor(self, listItem=None):
            self.busy = 1
            if not listItem == None:
                self.set_value(listItem)

            value = self.struct['performance']['settings']['cpu_governor']['value']
            if not value is None and not value == '':
                cpu_clusters = ["", "cpu0/", "cpu4/"]
                for cluster in cpu_clusters:
                    sys_device = '/sys/devices/system/cpu/' + cluster + 'cpufreq/scaling_governor'
                    if os.access(sys_device, os.W_OK):
                        cpu_governor_ctl = open(sys_device, 'w')
                        cpu_governor_ctl.write(value)
                        cpu_governor_ctl.close()

            self.busy = 0

    @log.log_function()
    def set_disk_park(self, listItem=None):
            self.busy = 1
            if not listItem == None:
                self.set_value(listItem)

            if self.struct['hdd']['settings']['disk_park']['value'] == '1':
                value = self.struct['hdd']['settings']['disk_park_time']['value']
                subprocess.call(("echo -e 'PARK_HDD=\"yes\"\nPARK_WAIT=\"%s\"' > /run/disk-park.dat") % value, shell=True)
            else:
                subprocess.call("rm -rf /run/disk-park.dat", shell=True)

            self.busy = 0

    @log.log_function()
    def set_disk_idle(self, listItem=None):
            self.busy = 1
            if not listItem == None:
                self.set_value(listItem)

            subprocess.call("killall hd-idle &> /dev/null", shell=True)
            if not self.struct['hdd']['settings']['disk_idle']['value'] == 'Disabled':
                for disk_idle_time in self.disk_idle_times:
                    if self.struct['hdd']['settings']['disk_idle']['value'] == disk_idle_time["name"]:
                        subprocess.call(("hd-idle -i %s") % disk_idle_time["value"], shell=True)

            self.busy = 0

    @log.log_function()
    def load_menu(self, focusItem):
            oe.winOeMain.build_menu(self.struct)

    @log.log_function()
    def set_value(self, listItem):
            self.struct[listItem.getProperty('category')]['settings'][listItem.getProperty('entry')]['value'] = listItem.getProperty('value')
            self.oe.write_setting('hardware', listItem.getProperty('entry'), unicode(listItem.getProperty('value')))
