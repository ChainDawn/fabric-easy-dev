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
import yaml

from config import peer, orderer, channel
from config.organization import Organization
from config.msp_support import static_msp_support

import logging
logger = logging.getLogger("config")

KEY_ORGANIZATIONS = "Organizations"
KEY_SYSTEM_CHANNEL = "SystemChannel"
KEY_USER_CHANNEL = "UserChannels"


class Network:

    def __init__(self, network_config, target_dir, msp_support_impl=static_msp_support):
        if not os.path.exists(network_config):
            raise ValueError("Network config file not exists: %s" % network_config)
        self.Dir = target_dir
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        with open(network_config, 'r') as conf:
            config_values = yaml.load(conf, yaml.CLoader)

        if KEY_ORGANIZATIONS not in config_values or len(config_values[KEY_ORGANIZATIONS]) == 0:
            raise Exception("No organization configuration found!!")

        if KEY_SYSTEM_CHANNEL not in config_values:
            raise Exception("No system channel configuration found!!")

        self.Organizations = {org["Name"]: Organization(self.Dir, msp_support_impl, **org)
                              for org in config_values[KEY_ORGANIZATIONS]}

        self.SysChannel = channel.SystemChannel(self.Dir, self.Organizations, **config_values[KEY_SYSTEM_CHANNEL])

    def deploy(self, interactive=False):
        peer_config_generator = peer.NodeBootstrapGenerator()
        orderer_config_generator = orderer.NodeBootstrapGenerator(self.SysChannel.GenesisBlock)
        for org in self.SysChannel.Orgs:
            org.deploy(peer_config_generator)
        for ord in self.SysChannel.Ords:
            ord.config(orderer_config_generator)

        if interactive:
            # TODO start interactive loop
            pass

    def boot(self):
        for org in self.SysChannel.Orgs:
            org.boot_peers()
        for ord in self.SysChannel.Ords:
            ord.boot()
        os.system("ps -ef | grep peer")
        os.system("ps -ef | grep orderer")

    def deploy_channel(self, channel_config_file, channel_name):
        if not os.path.exists(channel_config_file):
            raise ValueError("Channel config file not exists: %s" % channel_config_file)
        with open(channel_config_file, 'r') as conf:
            channel_config = yaml.load(conf, yaml.CLoader)
        if KEY_USER_CHANNEL not in channel_config:
            raise ValueError("No user channels config found in config file: %s" % channel_config_file)
        if channel_name not in channel_config[KEY_USER_CHANNEL]:
            raise ValueError("No channel name fond in channel config: %s" % channel_name)
        user_channel = channel.UserChannel(
            self.Dir, self.Organizations, **channel_config[KEY_USER_CHANNEL][channel_name])
        user_channel.deploy()

    def stop(self):
        for org in self.SysChannel.Orgs:
            org.stop_peers()
        for ord in self.SysChannel.Ords:
            ord.stop()
        os.system("ps -ef | grep peer")
        os.system("ps -ef | grep orderer")

    def clear(self):
        pass

    def down(self):
        pass
