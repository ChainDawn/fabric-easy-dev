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
        if not os.path.exists(peer_binary):
            raise Exception("Peer binary not found: %s" % peer_binary)

        self.config = api_config

        self.Dir = os.path.join(cache_dir, "cli-api-support")
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        self.Peer = os.path.join(self.Dir, "peer")
        os.system("cp %s %s" % (peer_binary, self.Peer))

        self.user_dir = os.path.join(self.Dir, self.config.User.MspId, self.config.User.Name)

        if not os.path.exists(self.user_dir):
            os.system("mkdir -p %s" % self.user_dir)

        __dump_cli_core_conf__(self.user_dir, self.config.User.MspId)
        os.system("cp -r %s/* %s" % (self.config.User.Dir, self.user_dir))

    def channel(self, channel):
        return CliChannelApi(channel, self)

    def chaincode_lifecycle(self):
        pass

    def chaincode(self):
        pass

    def __execute_api__(self, sub_command, func, *args):
        os.environ["FABRIC_CFG_PATH"] = self.user_dir
        return subprocess.call([self.Peer, sub_command, func, *args])


class CliChannelApi(api.ChannelApi, ABC):

    def __init__(self, channel, api_support):
        super(CliChannelApi, self).__init__()
        self.channel = channel
        self.support = api_support

    def create(self):
        block_file = os.path.join(self.support.Dir, "%s.block" % self.channel.Name)
        self.support.__execute_api__("channel", "create", *[
            "--channelID", self.channel.Name,
            "--file", self.channel.create_tx(self.support.Dir),
            "--orderer", self.support.config.Ord.deploy_handler.Address,
            "--tls",
            "--cafile", self.support.config.Ord.msp_holder.tls_ca(),
            "--outputBlock", block_file,
        ])

    def update(self):
        pass
