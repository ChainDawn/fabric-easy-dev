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
import logging
import os
import yaml
from orgconfig.msp import static_msp_support
from orgconfig.deploy import deploy_builder

KEY_ORGANIZATIONS = "Organizations"
KEY_PEERS = "Peers"
KEY_ORDERERS = "Orderers"
KEY_NAME = "Name"


class Node(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, org, msp_holder, deploy_build, **values):
        super(Node, self).__init__()
        self.update(values)
        self.Org = org
        self.Domain = "%s.%s" % (self.Name, self.Org.Domain)
        self.msp_holder = msp_holder
        self.deploy_handler = deploy_build(self, self.Org.Dir)


class Organization(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, target_dir, msp_support=static_msp_support, **values):
        super().__init__()
        self.update(values)

        self.logger = logging.getLogger("organization")

        self.Dir = os.path.join(target_dir, self.Name)
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        self.msp_support = msp_support(self)

        self.logger.info("Config organization: %s, mspid: %s" % (self.Name, self.MSPID))
        self.logger.debug("\tOrganization directory: %s" % self.Dir)

        self.msp_support.create_msp()

        msp_holder = self.msp_support.msp_holder
        self.PeerNodes = {n[KEY_NAME]: Node(self, msp_holder.node_msp_holder(n[KEY_NAME]), deploy_builder("Peer"), **n)
                          for n in self.Peers}
        self.OrdererNodes = {o[KEY_NAME]: Node(self, msp_holder.node_msp_holder(o[KEY_NAME]), deploy_builder("Orderer"), **o)
                             for o in self.Orderers}

    def deploy_peers(self):
        for peer in self.PeerNodes.values():
            peer.deploy_handler.deploy()

    def deploy_orderers(self, genesis_block):
        for orderer in self.OrdererNodes.values():
            orderer.deploy_handler.deploy(genesis_block)


def config_organizations(config_file, target_dir):
    if not os.path.exists(config_file):
        raise ValueError("Config file not exists: %s" % config_file)
    with open(config_file, 'r') as conf:
        raw_conf = yaml.load(conf, yaml.CLoader)
    if KEY_ORGANIZATIONS not in raw_conf:
        raise Exception("No organization found in config file: %s" % config_file)
    return {org["Name"]: Organization(target_dir, **org) for org in raw_conf[KEY_ORGANIZATIONS]}
