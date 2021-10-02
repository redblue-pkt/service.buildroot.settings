# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
# Copyright (C) 2020-present Team LibreELEC (https://libreelec.tv)

import os

################################################################################
# Base
################################################################################

XBMC_USER_HOME = os.environ.get('XBMC_USER_HOME', '/root/.kodi')
CONFIG_CACHE = os.environ.get('CONFIG_CACHE', '/root/.cache')
USER_CONFIG = os.environ.get('USER_CONFIG', '/root/.config')

################################################################################
# Connamn Module
################################################################################

connman = {
    'CONNMAN_DAEMON': '/usr/sbin/connmand',
    'WAIT_CONF_FILE': f'{CONFIG_CACHE}/libreelec/network_wait',
    'ENABLED': lambda : (True if os.path.exists(connman['CONNMAN_DAEMON']) and not os.path.exists('/dev/.kernel_ipconfig') else False),
    }
connman['ENABLED'] = connman['ENABLED']()

################################################################################
# Bluez Module
################################################################################

bluetooth = {
    'BLUETOOTH_DAEMON': '/usr/lib/bluetooth/bluetoothd',
    'OBEX_DAEMON': '/usr/lib/bluetooth/obexd',
    'ENABLED': lambda : (True if os.path.exists(bluetooth['BLUETOOTH_DAEMON']) else False),
    'D_OBEXD_ROOT': '/storage/downloads/',
    }
bluetooth['ENABLED'] = bluetooth['ENABLED']()

################################################################################
# Service Module
################################################################################

services = {
    'ENABLED': True,
    'KERNEL_CMD': '/proc/cmdline',
    'SAMBA_NMDB': '/usr/sbin/nmbd',
    'SAMBA_SMDB': '/usr/sbin/smbd',
    'D_SAMBA_WORKGROUP': 'WORKGROUP',
    'D_SAMBA_SECURE': '0',
    'D_SAMBA_USERNAME': 'root',
    'D_SAMBA_PASSWORD': 'root',
    'D_SAMBA_MINPROTOCOL': 'SMB2',
    'D_SAMBA_MAXPROTOCOL': 'SMB3',
    'D_SAMBA_AUTOSHARE': '1',
    'SSH_DAEMON': '/usr/sbin/dropbear',
    'OPT_SSH_NOPASSWD': "-B",
    'D_SSH_DISABLE_PW_AUTH': '0',
    'AVAHI_DAEMON': '/usr/sbin/avahi-daemon',
    'CRON_DAEMON': '/sbin/crond',
    }

system = {
    'ENABLED': True,
    'KERNEL_CMD': '/proc/cmdline',
    'SET_CLOCK_CMD': '/sbin/hwclock --systohc --utc',
    'XBMC_RESET_FILE': f'{CONFIG_CACHE}/reset_soft',
    'LIBREELEC_RESET_FILE': f'{CONFIG_CACHE}/reset_hard',
    'KEYBOARD_INFO': '/usr/share/X11/xkb/rules/base.xml',
    'UDEV_KEYBOARD_INFO': f'{CONFIG_CACHE}/xkb/layout',
    'NOX_KEYBOARD_INFO': '/usr/lib/keymaps',
    'BACKUP_DIRS': [
        XBMC_USER_HOME,
        USER_CONFIG,
        CONFIG_CACHE,
        '/root/.ssh',
        ],
    'BACKUP_FILTER' : [
        f'{XBMC_USER_HOME}/addons/packages',
        f'{XBMC_USER_HOME}/addons/temp',
        f'{XBMC_USER_HOME}/temp'
        ],
    'BACKUP_DESTINATION': '/root/backup/',
    'RESTORE_DIR': '/root/.restore/',
    'JOURNALD_CONFIG_FILE': '/root/.cache/journald.conf.d/00_settings.conf'
    }

updates = {
    'ENABLED': not os.path.exists('/dev/.update_disabled'),
    'UPDATE_REQUEST_URL': 'https://update.libreelec.tv/updates.php',
    'UPDATE_DOWNLOAD_URL': 'http://%s.libreelec.tv/%s',
    'LOCAL_UPDATE_DIR': '/root/.update/',

    'RPI_FLASHING_TRIGGER': '/root/.rpi_flash_firmware',
    }

about = {'ENABLED': True}

_services = {
    'sshd': ['dropbear.service'],
    'avahi': ['avahi-daemon.service'],
    'samba': ['nmbd.service', 'smbd.service'],
    'bluez': ['bluetooth.service'],
    'obexd': ['obex.service'],
    'crond': ['cron.service'],
    'iptables': ['iptables.service'],
    }
