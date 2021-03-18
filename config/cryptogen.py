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
        self.Specs = [{"Hostname": node.Name} for node in organization.Nodes]


class CryptoGenerator(yaml.YAMLObject):
    yaml_tag = "!Crypto-config"

    def __init__(self, cryptogen=env.CRYPTOGEN):
        self.PeerOrgs = None
        self.Command = cryptogen

    def generate(self, organization):
        return self.__execute__(organization, "generate")

    def extend(self, organization):
        return self.__execute__(organization, "extend")

    def __execute__(self, organization, sub_command):
        if organization.Dir is None or not os.path.exists(organization.Dir):
            raise ValueError("Organization working directory not exists: %s" % organization.Dir)

        self.PeerOrgs = [CryptoConfigItem(organization)]
        crypto_config_file = self.__dump__(organization.Dir, organization.MSPID)

        output = os.path.join(organization.Dir, organization.MSPID)
        command = [
            self.Command, sub_command,
            "--config=%s" % crypto_config_file,
            "--output=%s" % output
        ]
        if subprocess.call(command) != 0:
            raise Exception("Execute command error!")
        return output

    def __dump__(self, cache_dir, name):
        target_file = os.path.join(cache_dir, "%s-crypto-config.yaml" % name)
        index = 1
        while os.path.exists(target_file):
            target_file = os.path.join(cache_dir, "%s-crypto-config-%s.yaml" % (name, index))
            index = index + 1
        with open(target_file, "w") as target:
            yaml.dump(self, target)
        return target_file


class CryptogenMspPathSupport:

    def __init__(self, org_msp_dir, org_domain, check_exists=False):
        self.org_domain = org_domain
        self.basic_msp_dir = os.path.join(org_msp_dir, "peerOrganizations", org_domain)
        if check_exists and not os.path.exists(self.basic_msp_dir):
            raise Exception("Organization msp directory not exist: %s" % self.basic_msp_dir)

    def org_msp_dir(self):
        return os.path.join(self.basic_msp_dir, "msp")

    def node_msp_dir(self, node_name):
        return os.path.join(self.basic_msp_dir, "peers", "%s.%s" % (node_name, self.org_domain), "msp")

    def node_tls_dir(self, node_name):
        return os.path.join(self.basic_msp_dir, "peers", "%s.%s" % (node_name, self.org_domain), "tls")
