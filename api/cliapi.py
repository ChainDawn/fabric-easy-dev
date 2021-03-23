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
from config import env


def __dump_cli_core_conf__(target_dir, mspid, template=env.CLI_CORE_YAML_TEMPLATE):
    if not os.path.exists(template):
        raise ValueError("Cli core.yaml template file not exists: %s" % template)
    with open(template, "r") as template:
        template_yaml_data = yaml.load(template, yaml.CLoader)
    template_yaml_data["peer"]["localMspId"] = mspid
    with open(os.path.join(target_dir, "core.yaml"), "w") as target_file:
        yaml.dump(template_yaml_data, target_file)


class CliChannelApi(api.ChannelApi, ABC):

    def __init__(self, channel, peer_binary=env.PEER):
        super(CliChannelApi, self).__init__()
        self.peer = peer_binary
        self.channel = channel

        self.Dir = os.path.join(channel.Dir, "CLI")
        for org in self.channel.Orgs:
            target_dir = os.path.join(self.Dir, org.Name)
            if not os.path.exists(target_dir):
                os.system("mkdir -p %s" % target_dir)
            os.system("cp -r %s %s" % (org.admin_msp(), os.path.join(target_dir, "msp")))
            os.system("cp -r %s %s" % (org.admin_tls(), os.path.join(target_dir, "tls")))
            __dump_cli_core_conf__(target_dir, org.MSPID)

    def create(self, api_config, tx):
        api_peer = api_config.Prs[0]
        api_orderer = api_config.Ord
        os.environ["FABRIC_CFG_PATH"] = os.path.join(self.Dir, api_peer.Org.Name)
        os.environ["CORE_PEER_ADDRESS"] = api_peer.Address
        block_file = os.path.join(self.Dir, "%s.block" % self.channel.Name)
        subprocess.call([
            self.peer, "channel", "create",
            "--channelID", self.channel.Name,
            "--file", tx,
            "--orderer", api_orderer.Address,
            "--tls",
            "--cafile", api_orderer.Org.tlsca(),
            "--outputBlock", block_file,
        ])

    def update(self, tx):
        pass
