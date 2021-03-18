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
import subprocess
from config import daemon


class BaseConfigModel(dict):

    def __getattr__(self, item):
        return self[item]


class Node(BaseConfigModel):

    def __init__(self, organization, **source):
        super().__init__()
        self.update(source)
        self.MSPID = organization.MSPID
        self.OrgName = organization.Name
        self.Domain = "%s.%s" % (self.Name, organization.Domain)
        self.Address = "%s:%s" % (self.Domain, self.ListenPort)
        self.ListenAddress = "0.0.0.0:%s" % self.ListenPort
        self.OperationsListenAddress = "127.0.0.1:%s" % self.OperationsListenPort
        try:
            self.ChaincodeListenAddress = "0.0.0.0:%s" % self.ChaincodeListenPort
        except KeyError:
            pass

    def __config_node__(self, base_dir, command_binary, msp_dir, tls_dir, boot_command):
        node_dir = self.__mkdir__(base_dir)
        os.system("cp -r %s %s" % (msp_dir, os.path.join(node_dir, "msp")))
        os.system("cp -r %s %s" % (tls_dir, os.path.join(node_dir, "tls")))
        os.system("cp %s %s" % (command_binary, node_dir))
        daemon.config_daemon(node_dir, "%s-peer-node$%s" % (self.OrgName, self.Name), boot_command)
        return node_dir

    def config_peer(self, base_dir, peer_binary, msp_dir, tls_dir, gossip_bootstrap, config_generator):
        node_dir = self.__config_node__(base_dir, peer_binary, msp_dir, tls_dir, "peer node start")
        config_generator.generate(self, node_dir, gossip_bootstrap)

    def config_orderer(self, base_dir, orderer_binary, msp_dir, tls_dir, genesis_block, config_generator):
        node_dir = self.__config_node__(base_dir, orderer_binary, msp_dir, tls_dir, "orderer")
        os.system("cp %s %s" % (genesis_block, os.path.join(node_dir, "genesis.block")))
        config_generator.generate(self, node_dir)

    def __mkdir__(self, base_dir):
        node_dir = os.path.join(base_dir, self.Name)
        if os.path.exists(node_dir):
            raise Exception("Target node directory already exist: %s" % node_dir)
        os.system("mkdir -p %s" % node_dir)
        return node_dir


class Organization(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Nodes" in source:
            self.Nodes = [Node(self, **item) for item in source["Nodes"]]
        self.Dir = None
        self.MspDir = None

    def build(self, target_dir, msp_generator):
        self.Dir = os.path.join(target_dir, self.Name)
        if os.path.exists(self.Dir):
            if self.__check_exist_msp__():
                self.MspDir = os.path.join(self.Dir, self.MSPID, "msp")
                return
            raise Exception("Target organization directory already exist: %s" % self.Dir)
        subprocess.call(["mkdir", "-p", self.Dir])
        self.MspDir = msp_generator.generate(self)

    def extend_msp(self, msp_generator):
        return msp_generator.extend(self)

    def __check_exist_msp__(self):
        if not os.path.exists(os.path.join(self.Dir, self.MSPID)):
            return False
        return True


class Config(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Organizations" in source:
            self.Organizations = [Organization(**item) for item in source["Organizations"]]

    def generate_msp(self, target_dir):
        for organization in self.Organizations:
            organization.build(target_dir)
