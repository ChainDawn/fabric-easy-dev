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

import env


class BaseConfigModel(dict):

    def __getattr__(self, item):
        return self[item]


class Node(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)

    def generate_peer_config(self, target_dir):
        pass

    def generate_orderer_config(self, target_dir):
        pass


class Organization(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Nodes" in source:
            self.Nodes = [Node(**item) for item in source["Nodes"]]

    def generate_msp(self, target_dir=env.TARGET_DIR):
        return CryptoConfig(self).generate(self.dir(target_dir))

    def extend_msp(self, target_dir):
        return CryptoConfig(self).extend(target_dir)

    def dir(self, base_dir):
        o_dir = os.path.join(base_dir, self.Name)
        if not os.path.exists(o_dir):
            subprocess.call(["mkdir", "-p", o_dir])
        return o_dir


class CryptoConfigItem(yaml.YAMLObject):

    def __init__(self, organization):
        self.Name = organization.MSPID
        self.Domain = organization.Domain
        self.Specs = [{"Hostname": node.Name} for node in organization.Nodes]


class CryptoConfig(yaml.YAMLObject):
    yaml_tag = "!Crypto-config"

    def __init__(self, organization):
        self.PeerOrgs = [CryptoConfigItem(organization)]

    def name(self):
        return self.PeerOrgs[0].Name

    def domain(self):
        return self.PeerOrgs[0].Domain

    def generate(self, target_dir):
        crypto_config_file = self.__dump__(target_dir)
        output = os.path.join(target_dir, self.name())
        subprocess.call([env.CRYPTOGEN, "generate", "--config=%s" % crypto_config_file, "--output=%s" % output])
        os.system("mv %s/peerOrganizations/%s/* %s" % (output, self.domain(), output))
        os.system("rm -fr %s" % os.path.join(output, "peerOrganizations"))
        os.system("mv %s %s" % (os.path.join(output, "peers"), os.path.join(output, "nodes")))

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
            organization.generate_msp(target_dir)


with open("../sampleconfigs/config.yaml", 'r') as configFile:
    data = yaml.safe_load(configFile)

config = Config(**data)

for org in config.Organizations:
    org.generate_msp()
