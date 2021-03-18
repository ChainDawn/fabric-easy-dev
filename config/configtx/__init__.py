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
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import yaml
from config import env
from config.configtx.policy import Policy
from config.configtx.organization import Organization
from config.configtx.application import Application
from config.configtx.orderer import Orderer, EtcdRaft, Consenter


def __channel_capabilities__():
    return {
        "V2.0": "true"
    }


def __channel_policies__():
    return {
        "Readers":              Policy("ImplicitMeta", "ANY Readers"),
        "Writers":              Policy("ImplicitMeta", "ANY Writers"),
        "Admins":               Policy("ImplicitMeta", "MAJORITY Admins"),
    }


class SystemChannelProfile(yaml.YAMLObject):

    def __init__(self, application, orderer, consortiums):
        self.Application = application
        self.Capabilities = __channel_capabilities__()
        self.Consortiums = consortiums
        self.Orderer = orderer
        self.Policies = __channel_policies__()


class UserChannelProfile(yaml.YAMLObject):

    def __init__(self, application, consortium):
        self.Application = application
        self.Capabilities = __channel_capabilities__()
        self.Consortium = consortium
        self.Policies = __channel_policies__()


class Profiles(yaml.YAMLObject):

    def __init__(self, profiles):
        self.Profiles = profiles

    def __dump__(self, cache_dir=env.CACHE_DIR):
        with open(os.path.join(cache_dir, "configtx.yaml"), "w") as configtx:
            yaml.dump(self, configtx)

    def generateSystemGenesisBlock(self, profile_name, sys_channel_name, target_dir):
        pass

    def generateCreateChannelTx(self, profile_name, channel_name, target_dir):
        pass


class SystemChannel:

    def __init__(self, orgs, orderer_nodes):
        self.Organizations = orgs

    def generate_genesis_block(self, target_dir):
        pass


def config_system_channel(org_configs, consenter_nodes):
    orgs = [Organization(o.Name, o.MSPID, o.MspDir) for o in org_configs]
    app = Application(orgs)

    consenters = [Consenter(node, "/Users/yiwenlong/Code/fabric-easy-dev/target/Org1/Org1MSP/tlsca/tlsca.org1.fnodocker.icu-cert.pem") for node in consenter_nodes]
    etcdraft = EtcdRaft(consenters)
    addresses = [node.Address for node in consenter_nodes]
    orderer = Orderer(etcdraft, addresses)

    consortiums = {"SimpleCOnsortiums": {"Organizations": orgs}}

    sys_channel_profile = SystemChannelProfile(app, orderer, consortiums)
    pfs = Profiles({"SystemChannelProfile": sys_channel_profile})
    pfs.__dump__()


def config_user_channel():
    pass
