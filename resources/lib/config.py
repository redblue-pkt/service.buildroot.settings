# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2020-present Team LibreELEC

import os
import os_tools

OS_RELEASE = os_tools.read_shell_settings('/etc/os-release')

CONFIG_CACHE = os.environ.get('CONFIG_CACHE', '/root/.cache')
USER_CONFIG = os.environ.get('USER_CONFIG', '/root/.config')

HOSTNAME = '/etc/hostname'
HOSTS_CONF = '/etc/hosts'

REGDOMAIN_CONF = '/etc/regdomain.conf'
SETREGDOMAIN = '/usr/lib/iw/setregdomain'
