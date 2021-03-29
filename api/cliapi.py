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
from abc import ABC

import api
import os
import subprocess
import yaml
import env


def __dump_cli_core_conf__(target_dir, mspid, template=env.CLI_CORE_YAML_TEMPLATE):
    if not os.path.exists(template):
        raise ValueError("Cli core.yaml template file not exists: %s" % template)
    with open(template, "r") as template:
        template_yaml_data = yaml.load(template, yaml.CLoader)
    template_yaml_data["peer"]["localMspId"] = mspid
    with open(os.path.join(target_dir, "core.yaml"), "w") as target_file:
        yaml.dump(template_yaml_data, target_file)


class CliApiSupport(api.ApiSupport, ABC):

    def __init__(self, api_config, cache_dir, peer_binary=env.PEER):
        self.api_config = api_config
        self.Dir = os.path.join(cache_dir, "cli-api-support")
        self.peer = peer_binary
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

    def channel(self, channel):
        pass

    def chaincode_lifecycle(self):
        pass

    def chaincode(self):
        pass

    def __execute_api__(self, sub_command, func, *args):
        return subprocess.call([self.peer, sub_command, func, *args])


class CliChannelApi(api.ChannelApi, ABC):

    def __init__(self, channel, api_support):
        super(CliChannelApi, self).__init__()
        self.channel = channel
        self.api_support = api_support

    def create(self):
        block_file = os.path.join(self.api_support.Dir, "%s.block" % self.channel.Name)

        self.api_support.__execute_api__("channel", "create", *[
            "--channelID", self.channel.Name,
            "--file", self.channel.create_tx(self.api_support.Dir),
            "--orderer", self.api_support.api_config.orderer.Address,
            "--tls",
            "--cafile", self.api_support.api_config.orderer.Org.tlsca(),
            "--outputBlock", block_file,
        ])

    def update(self):
        pass
