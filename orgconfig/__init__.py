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
from utils.fileutil import mkdir_if_need

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
        self.FullName = "%s.%s" % (self.Org.Name, self.Name)


class Organization(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, target_dir, msp_support=static_msp_support, **values):
        super().__init__()
        self.update(values)

        self.logger = logging.getLogger("organization")

        self.Dir = os.path.join(target_dir, self.Name)
        mkdir_if_need(self.Dir)

        self.msp_support = msp_support(self)

        self.logger.debug("Config organization: %s, mspid: %s" % (self.Name, self.MSPID))
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

    def msp_dir(self):
        return self.msp_support.msp_holder.org_msp_dir

    def admin(self):
        return self.msp_support.msp_holder.admin_msp_holder()


def config_organizations(raw_conf, target_dir):
    return {org["Name"]: Organization(target_dir, **org) for org in raw_conf}


def find_node(org_map, node):
    org_name, node_name = str(node).split(".")
    if org_name not in org_map:
        raise ValueError("Organization not found: %s" % org_name)
    org = org_map[org_name]
    if node_name in org.PeerNodes:
        return org.PeerNodes[node_name]
    if node_name in org.OrdererNodes:
        return org.OrdererNodes[node_name]
    raise ValueError("Node not found: %s" % node)


def find_user(org_map, user):
    org_name, user_name = str(user).split(".")
    if org_name not in org_map:
        raise ValueError("Organization not found: %s" % org_name)
    org = org_map[org_name]
    return org.msp_support.msp_holder.user_msp_holder(user_name)
