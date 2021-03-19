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

from config import env


class CryptoConfigItem(yaml.YAMLObject):

    def __init__(self, organization):
        self.Name = organization.MSPID
        self.Domain = organization.Domain
        self.Specs = [{"Hostname": node["Name"]} for node in organization.Nodes]


class CryptoGenerator(yaml.YAMLObject):
    yaml_tag = "!Crypto-config"

    def __init__(self):
        self.PeerOrgs = None

    def generate(self, org):
        return self.__execute__(org, "generate")

    def extend(self, org):
        return self.__execute__(org, "extend")

    def __execute__(self, org, sub_command, cryptogen=env.CRYPTOGEN):
        if org.Dir is None or not os.path.exists(org.Dir):
            raise ValueError("Organization working directory not exists: %s" % org.Dir)

        self.PeerOrgs = [CryptoConfigItem(org)]
        crypto_config_file = self.__dump__(org.Dir, org.MSPID)
        command = [
            cryptogen, sub_command,
            "--config=%s" % crypto_config_file,
            "--output=%s" % org.MspBaseDir
        ]
        if subprocess.call(command) != 0:
            raise Exception("Execute command error!")

    def __dump__(self, cache_dir, name):
        target_file = os.path.join(cache_dir, "%s-crypto-config.yaml" % name)
        index = 1
        while os.path.exists(target_file):
            target_file = os.path.join(cache_dir, "%s-crypto-config-%s.yaml" % (name, index))
            index = index + 1

        with open(target_file, "w") as target:
            yaml.dump(self, target)
        return target_file


class StaticOrganizationMspHolder:

    def __init__(self, organization):
        self.Org = organization
        self.org_crypto_dir = os.path.join(organization.MspBaseDir, "peerOrganizations", organization.Domain)
        self.org_msp_dir = os.path.join(self.org_crypto_dir, "msp")
        self.org_ca_dir = os.path.join(self.org_crypto_dir, "ca")
        self.org_nodes_dir = os.path.join(self.org_crypto_dir, "peers")
        self.org_tlsca_dir = os.path.join(self.org_nodes_dir, "tlsca")
        self.org_users_dir = os.path.join(self.org_nodes_dir, "users")

    def node_msp(self, node_name):
        return os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.Org.Domain), "msp")

    def node_tls(self, node_name):
        return os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.Org.Domain), "tls")

    def msp_dir(self):
        return self.org_msp_dir

    def check(self):
        return os.path.exists(self.org_msp_dir)

    def node_server_tls_cert(self, node_name):
        return os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.Org.Domain), "tls", "server.crt")
