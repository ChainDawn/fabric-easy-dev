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

import yaml


class BaseConfigModel(dict):

    def __getattr__(self, item):
        return self[item]


class Node(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)

    def generate_peer_config(self, target_dir, core_yaml_template, mspid, gossip_bootstrap):
        with open(core_yaml_template, 'r') as template:
            core_yaml_data = yaml.load(template, yaml.CLoader)
        # modify
        core_yaml_data["peer"]["listenAddress"] = "0.0.0.0:%s" % self.ListenPort
        core_yaml_data["peer"]["address"] = "0.0.0.0:%s" % self.ListenPort
        core_yaml_data["peer"]["chaincodeListenAddress"] = "0.0.0.0:%s" % self.ChaincodeListenPort
        core_yaml_data["peer"]["gossip"]["bootstrap"] = gossip_bootstrap
        core_yaml_data["peer"]["localMspId"] = mspid
        core_yaml_data["operations"]["listenAddress"] = "127.0.0.1:%s" % self.OperationsListenPort
        # dump into target directory.
        with open(os.path.join(target_dir, "core.yaml"), 'w') as target_file:
            yaml.dump(core_yaml_data, target_file)

    def generate_orderer_config(self, target_dir):
        pass

    def config_peer(self, base_dir, peer_binary, core_yaml_template, msp_dir, tls_dir, mspid, gossip_bootstrap):
        node_dir = os.path.join(base_dir, self.Name)
        if os.path.exists(node_dir):
            raise Exception("Target node directory already exist: %s" % node_dir)
        os.system("mkdir -p %s" % node_dir)
        os.system("cp -r %s %s" % (msp_dir, os.path.join(node_dir, "msp")))
        os.system("cp -r %s %s" % (tls_dir, os.path.join(node_dir, "tls")))
        os.system("cp %s %s" % (peer_binary, node_dir))
        self.generate_peer_config(node_dir, core_yaml_template, mspid, gossip_bootstrap)

    def config_orderer(self, target_dir, mspid, msp_dir, tls_dir, genesis_block):
        pass


class Organization(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Nodes" in source:
            self.Nodes = [Node(**item) for item in source["Nodes"]]
        self.Dir = None
        self.MspDir = None

    def build(self, target_dir, msp_generator):
        self.Dir = os.path.join(target_dir, self.Name)
        if os.path.exists(self.Dir):
            raise Exception("Target organization directory already exist: %s" % self.Dir)
        subprocess.call(["mkdir", "-p", self.Dir])
        self.MspDir = msp_generator.generate(self)

    def extend_msp(self, target_dir):
        return CryptoConfig(self).extend(target_dir)


class CryptoConfigItem(yaml.YAMLObject):

    def __init__(self, organization):
        self.Name = organization.MSPID
        self.Domain = organization.Domain
        self.Specs = [{"Hostname": node.Name} for node in organization.Nodes]


class CryptoConfig(yaml.YAMLObject):
    yaml_tag = "!Crypto-config"

    def __init__(self, cryptogen):
        self.PeerOrgs = None
        self.Command = cryptogen

    def name(self):
        return self.PeerOrgs[0].Name

    def domain(self):
        return self.PeerOrgs[0].Domain

    def generate(self, organization):
        self.PeerOrgs = [CryptoConfigItem(organization)]
        crypto_config_file = self.__dump__(organization.Dir)
        output = os.path.join(organization.Dir, self.name())
        subprocess.call([self.Command, "generate", "--config=%s" % crypto_config_file, "--output=%s" % output])
        os.system("mv %s/peerOrganizations/%s/* %s" % (output, self.domain(), output))
        os.system("rm -fr %s" % os.path.join(output, "peerOrganizations"))
        os.system("mv %s %s" % (os.path.join(output, "peers"), os.path.join(output, "nodes")))
        return output

    def extend(self, target_dir):
        pass

    def __dump__(self, cache_dir):
        target_file = os.path.join(cache_dir, "%s-crypto-config.yaml" % self.name())
        with open(target_file, "w") as target:
            yaml.dump(self, target)
        return target_file


class SystemChannel(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Organizations" in source:
            self.Organizations = [Organization(**item) for item in source["Organizations"]]
        if "Orderers" in source:
            self.Orderers = [Node(**item) for item in source["Orderers"]]

    def generate_genesis_block(self, target_dir):
        pass


class Config(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Organizations" in source:
            self.Organizations = [Organization(**item) for item in source["Organizations"]]
        if "SystemChannel" in source:
            self.SystemChannel = SystemChannel(**source["SystemChannel"])

    def generate_msp(self, target_dir):
        for organization in self.Organizations:
            organization.build(target_dir)
