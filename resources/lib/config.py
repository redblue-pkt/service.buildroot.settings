# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import os
import os_tools

OS_RELEASE = os_tools.read_shell_settings('/etc/os-release')

HOME = os.environ.get('HOME', '/root')
XDG_CACHE_HOME = os.environ.get('XDG_CACHE_HOME', os.path.join(HOME, '.cache'))
XDG_CONFIG_HOME = os.environ.get(
    'XDG_CONFIG_HOME', os.path.join(HOME, '.config'))
XDG_RUNTIME_DIR = os.environ.get('XDG_RUNTIME_DIR' '/run')

HOSTNAME = '/etc/hostname'
HOSTS_CONF = '/etc/hosts'

REGDOMAIN_CONF = '/etc/regdomain.conf'
SETREGDOMAIN = '/usr/lib/iw/setregdomain'
