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
import env
from orgconfig.deploy.daemon import DaemonProcessHandler
from orgconfig.deploy.nodeconfig import config_core_yaml, config_orderer_yaml


class NodeDeployHandler:

    def __init__(self, node, deploy_dir):
        self.Node = node
        self.Dir = os.path.join(deploy_dir, self.Node.Name)
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        os.system("cp -r %s/* %s" % (self.Node.msp_holder.Dir, self.Dir))

    def __init_basic_addresses__(self, domain, listen_port, operations_port):
        self.Address = "%s:%s" % (domain, listen_port)
        self.ListenAddress = "0.0.0.0:%s" % listen_port
        self.OperationsListenAddress = "0.0.0.0:%s" % operations_port

    def __init_process_handler__(self, command):
        self.proc_handler = DaemonProcessHandler(self.Dir, "%s-%s" % (self.Node.Org.Name, self.Node.Name), command)


class PeerDeployHandler(NodeDeployHandler):

    def __init__(self, node, deploy_dir):
        super().__init__(node, deploy_dir)
        self.ListenPort, self.OperationsPort, self.ChaincodePort = str(node.Ports).split(", ")
        self.__init_basic_addresses__(self.Node.Domain, self.ListenPort, self.OperationsPort)
        self.ChaincodeListenAddress = "0.0.0.0:%s" % self.ChaincodePort
        self.__init_process_handler__("peer node start")

    def deploy(self, peer_binary=env.PEER):
        if not os.path.exists(peer_binary):
            raise ValueError("Peer command binary file not exists: %s" % peer_binary)
        os.system("cp %s %s" % (peer_binary, self.Dir))
        config_core_yaml(self)

    def gossip_bootstrap_address(self):
        return self.Node.Org.PeerNodes[self.Node.GossipNode].deploy_handler.Address


class OrdererDeployHandler(NodeDeployHandler):

    def __init__(self, node, deploy_dir):
        super().__init__(node, deploy_dir)
        self.ListenPort, self.OperationsPort = str(node.Ports).split(", ")
        self.__init_basic_addresses__(node.Domain, self.ListenPort, self.OperationsPort)
        self.OperationsListenAddress = "0.0.0.0:%s" % self.OperationsPort
        self.__init_process_handler__("orderer")

    def deploy(self, genesis_block, orderer_binary=env.ORDERER):
        if genesis_block is None or not os.path.exists(genesis_block):
            raise ValueError("Genesis block file not exists: %s" % genesis_block)
        os.system("cp %s %s" % (genesis_block, self.Dir))
        if not os.path.exists(orderer_binary):
            raise ValueError("Orderer command binary file not exists: %s" % orderer_binary)
        os.system("cp %s %s" % (orderer_binary, self.Dir))
        config_orderer_yaml(self)


def deploy_builder(node_type):
    if node_type == "Peer":
        def pf(node, deploy_dir):
            return PeerDeployHandler(node, deploy_dir)
        return pf
    if node_type == "Orderer":
        def of(node, deploy_dir):
            return OrdererDeployHandler(node, deploy_dir)
        return of
