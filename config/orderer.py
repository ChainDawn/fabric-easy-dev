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

    def __init__(self, genesis_block_source, template=env.ORDERER_YAML_TEMPLATE, orderer_binary=env.ORDERER):
        if not os.path.exists(template):
            raise ValueError("Template file not exists: %s" % template)
        self.template = template

        if not os.path.exists(genesis_block_source):
            raise ValueError("Genesis block file not exists: %s" % genesis_block_source)
        self.genesis_block_source = genesis_block_source

        if not os.path.exists(orderer_binary):
            raise ValueError("Orderer binary fil not exists: %s" % orderer_binary)
        self.binary = orderer_binary
        self.command = "orderer"

    def config(self, node):
        with open(self.template, 'r') as template:
            orderer_yaml_data = yaml.load(template, yaml.CLoader)

        orderer_yaml_data["General"]["ListenPort"] = node.ListenPort
        orderer_yaml_data["General"]["localMspId"] = node.Org.MSPID
        orderer_yaml_data["Operations"]["listenAddress"] = node.OperationsListenAddress

        # dump into target directory.
        target_file_path = os.path.join(node.Dir, "orderer.yaml")
        with open(target_file_path, 'w') as target_file:
            yaml.dump(orderer_yaml_data, target_file)

        os.system("cp %s %s" % (self.genesis_block_source, os.path.join(node.Dir, "genesis.block")))
        os.system("cp %s %s" % (self.binary, node.Dir))
        return daemon.config_daemon(node.Dir, node.process_label(), self.command)

    @staticmethod
    def check_config(node):
        if os.path.exists(os.path.join(node.Dir, "orderer.yaml")) and \
                os.path.exists(os.path.join(node.Dir, "orderer")) and \
                os.path.exists(os.path.join(node.Dir, "genesis.block")) and \
                daemon.check_config(node.Dir):
            return daemon.NodeProcessHandler(node.Dir, node.process_label())
        return None
