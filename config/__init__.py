# -*- encoding: utf-8 -*-
#
# Copyright 2020 Yiwenlong(wlong.yi#gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import sys
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.organization import Organization
from config.msp_support import static_msp_support

KEY_ORGANIZATIONS = "Organizations"
KEY_SYSTEM_CHANNEL = "SystemChannel"


class Network:

    def __init__(self, network_config, target_dir, msp_support_impl=static_msp_support):
        if not os.path.exists(network_config):
            raise ValueError("Network config file not exists: %s" % network_config)
        if not os.path.exists(target_dir):
            os.system("mkdir -p %s" % target_dir)

        with open(network_config, 'r') as config:
            config_values = yaml.load(config, yaml.CLoader)

        if KEY_ORGANIZATIONS not in config_values or len(config_values[KEY_ORGANIZATIONS]) == 0:
            raise Exception("No organization configuration found!!")

        if KEY_SYSTEM_CHANNEL not in config_values:
            raise Exception("No system channel configuration found!!")

        self.Organizations = {org["Name"]: Organization(target_dir, msp_support_impl, **org)
                              for org in config_values[KEY_ORGANIZATIONS]}

    def deploy(self, interactive=False):
        pass

    def boot(self):
        pass

    def stop(self):
        pass

    def clear(self):
        pass

    def down(self):
        pass
