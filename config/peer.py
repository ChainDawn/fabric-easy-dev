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

from config import daemon, env


class NodeBootstrapGenerator:

    def __init__(self, template=env.CORE_YAML_TEMPLATE, peer_binary=env.PEER):
        if not os.path.exists(template):
            raise ValueError("Template file not exists: %s" % template)
        self.template = template
        if not os.path.exists(peer_binary):
            raise ValueError("Peer binary not exists: %s" % peer_binary)
        self.binary = peer_binary
        self.command = "peer node start"

    def config(self, node):
        with open(self.template, 'r') as template:
            core_yaml_data = yaml.load(template, yaml.CLoader)

        # modify
        core_yaml_data["peer"]["listenAddress"] = node.ListenAddress
        core_yaml_data["peer"]["address"] = node.ListenAddress
        core_yaml_data["peer"]["chaincodeListenAddress"] = node.ChaincodeListenAddress
        core_yaml_data["peer"]["gossip"]["bootstrap"] = node.gossip_bootstrap_address()
        core_yaml_data["peer"]["localMspId"] = node.Org.MSPID
        core_yaml_data["operations"]["listenAddress"] = node.OperationsListenAddress

        # dump into target directory.
        with open(os.path.join(node.Dir, "core.yaml"), 'w') as target_file:
            yaml.dump(core_yaml_data, target_file)

        os.system("cp %s %s" % (self.binary, node.Dir))
        return daemon.config_daemon(node.Dir, node.process_label(), self.command)

    @staticmethod
    def check_config(node):
        if os.path.exists(os.path.join(node.Dir, "core.yaml")) and \
                os.path.exists(os.path.join(node.Dir, "peer")) and \
                daemon.check_config(node.Dir):
            return daemon.NodeProcessHandler(node.Dir, node.process_label())
        return None
