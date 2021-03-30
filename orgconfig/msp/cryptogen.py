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
import logging

import env


class CryptoConfigItem(yaml.YAMLObject):

    def __init__(self, organization):
        self.Name = organization.MSPID
        self.Domain = organization.Domain
        nodes = organization.Peers + organization.Orderers
        self.Specs = [{"Hostname": node["Name"]} for node in nodes]


class CryptoGenerator(yaml.YAMLObject):

    def __init__(self):
        self.PeerOrgs = None
        self.logger = logging.getLogger("cryptogen")

    def generate(self, msp_support, cryptogen=env.CRYPTOGEN):
        self.logger.info("Generate msp for organization: %s" % msp_support.org.Name)

        self.logger.debug("\tCryptogen binary: %s" % cryptogen)
        crypto_config_file = self.__dump__(msp_support)
        self.logger.debug("\tCrypto config file: %s" % crypto_config_file)
        self.logger.debug("\tTarget directory: %s" % crypto_config_file)

        command = [cryptogen, "generate", "--config=%s" % crypto_config_file, "--output=%s" % msp_support.Dir]
        if subprocess.call(command) != 0:
            raise Exception("Execute command error!")

    def extend(self, msp_support, cryptogen=env.CRYPTOGEN):
        self.logger.info("Extend msp for organization: %s" % msp_support.org.Name)
        self.logger.debug("\tCryptogen binary: %s" % cryptogen)
        crypto_config_file = self.__dump__(msp_support)
        self.logger.debug("\tCrypto config file: %s" % crypto_config_file)
        self.logger.debug("\tTarget directory: %s" % crypto_config_file)

        command = [cryptogen, "extend", "--config=%s" % crypto_config_file, "--input=%s" % msp_support.Dir]
        if subprocess.call(command) != 0:
            raise Exception("Execute command error!")

    def __dump__(self, msp_support):
        self.PeerOrgs = [CryptoConfigItem(msp_support.org)]
        target_file = os.path.join(msp_support.config_cache_dir, "%s-crypto.yaml" % msp_support.org.MSPID)
        index = 1
        while os.path.exists(target_file):
            target_file = os.path.join(msp_support.config_cache_dir, "%s-crypto-%s.yaml" % (msp_support.org.MSPID, index))
            index = index + 1

        with open(target_file, "w") as target:
            yaml.dump(self, target)
        return target_file


class StubMspHolder:

    def __init__(self, name, org_domain, msp_id, base_dir):
        self.Name = name
        self.OrgDomain = org_domain
        self.MspId = msp_id
        self.Dir = base_dir
        if not os.path.exists(self.Dir):
            raise ValueError("Msp holder directory not exists: %s" % self.Dir)

    def tls_crt(self):
        return os.path.join(self.Dir, "tls", "server.crt")

    def tls_ca(self):
        return os.path.join(self.Dir, "tls", "ca.crt")


class StaticOrganizationMspHolder:

    def __init__(self, org_domain, msp_id, msp_dir):
        self.org_domain = org_domain
        self.msp_id = msp_id
        self.org_crypto_dir = os.path.join(msp_dir, "peerOrganizations", self.org_domain)
        self.org_msp_dir = os.path.join(self.org_crypto_dir, "msp")
        self.org_ca_dir = os.path.join(self.org_crypto_dir, "ca")
        self.org_nodes_dir = os.path.join(self.org_crypto_dir, "peers")
        self.org_tlsca_dir = os.path.join(self.org_crypto_dir, "tlsca")
        self.org_users_dir = os.path.join(self.org_crypto_dir, "users")
        self.check_dirs = [
            self.org_crypto_dir, self.org_msp_dir, self.org_ca_dir, self.org_nodes_dir,
            self.org_tlsca_dir, self.org_users_dir
        ]

    def check(self):
        for check_item in self.check_dirs:
            if not os.path.exists(check_item):
                return False
        return True

    def node_msp_holder(self, node_name):
        node_msp_dir = os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.org_domain))
        if not os.path.exists(node_msp_dir):
            raise Exception("Node not found: %s" % node_name)
        return StubMspHolder(node_name, self.org_domain, self.msp_id, node_msp_dir)

    def user_msp_holder(self, user_name):
        user_msp_dir = os.path.join(self.org_users_dir, "%s@%s" % (user_name, self.org_domain))
        if not os.path.exists(user_msp_dir):
            raise Exception("User not found: %s" % user_name)
        return StubMspHolder(user_name, self.org_domain, self.msp_id, user_msp_dir)

    def admin_msp_holder(self):
        return self.user_msp_holder("Admin")


class StaticMspSupport:

    def __init__(self, org):
        self.org = org
        self.Dir = os.path.join(org.Dir, "static-msp-support")
        self.logger = logging.getLogger("msp")
        self.config_cache_dir = org.Dir
        self.msp_holder = StaticOrganizationMspHolder(org_domain=org.Domain, msp_id=org.MSPID, msp_dir=self.Dir)
        self.msp_generator = CryptoGenerator()

        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

    def create_msp(self, auto_extend=False):
        if self.msp_holder.check():
            self.logger.info("Msp files already exists: %s" % self.msp_holder.org_crypto_dir)
            if auto_extend:
                self.msp_generator.extend(self)
            return
        self.msp_generator.generate(self)
