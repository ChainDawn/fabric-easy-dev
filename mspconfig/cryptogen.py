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

from config import env


class CryptoConfigItem(yaml.YAMLObject):

    def __init__(self, organization):
        self.Name = organization.MSPID
        self.Domain = organization.Domain
        self.Specs = [{"Hostname": node} for node in organization.Nodes]


class CryptoGenerator(yaml.YAMLObject):

    def __init__(self):
        self.PeerOrgs = None
        self.logger = logging.getLogger("cryptogen")

    def generate(self, msp_support):
        self.logger.info("Generate msp for organization: %s" % msp_support.org.Name)
        return self.__execute__(msp_support.org, "generate", msp_support.config_cache_dir, msp_support.Dir)

    def extend(self, msp_support):
        self.logger.info("Extend msp for organization: %s" % msp_support.org.Name)
        return self.__execute__(msp_support.org, "extend", msp_support.config_cache_dir, msp_support.Dir)

    def __execute__(self, org, sub_command, config_cache_dir, output_dir, cryptogen=env.CRYPTOGEN):
        self.logger.debug("\tCryptogen binary: %s" % cryptogen)
        self.PeerOrgs = [CryptoConfigItem(org)]

        crypto_config_file = self.__dump__(config_cache_dir, org.MSPID)
        self.logger.debug("\tCrypto config file: %s" % crypto_config_file)
        self.logger.debug("\tTarget directory: %s" % crypto_config_file)

        command = [cryptogen, sub_command, "--config=%s" % crypto_config_file, "--input=%s" % output_dir]
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

    def __init__(self, org_domain, msp_dir):
        self.org_domain = org_domain
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

    def node_msp(self, node_name):
        return os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.org_domain), "msp")

    def node_tls(self, node_name):
        return os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.org_domain), "tls")

    def msp_dir(self):
        return self.org_msp_dir

    def node_server_tls_cert(self, node_name):
        return os.path.join(self.org_nodes_dir, "%s.%s" % (node_name, self.org_domain.Domain), "tls", "server.crt")

    def admin_msp(self):
        return os.path.join(self.org_users_dir, "Admin@%s" % self.org_domain, "msp")

    def admin_tls(self):
        return os.path.join(self.org_users_dir, "Admin@%s" % self.org_domain, "tls")

    def tlsca(self):
        return os.path.join(self.org_tlsca_dir, "tlsca.%s-cert.pem" % self.org_domain)


class StaticMspSupport:

    def __init__(self, org):
        self.org = org
        self.Dir = os.path.join(org.Dir, "static-msp-support")
        self.logger = logging.getLogger("msp")
        self.config_cache_dir = org.Dir
        self.msp_holder = StaticOrganizationMspHolder(org_domain=org.Domain, msp_dir=self.Dir)
        self.msp_generator = CryptoGenerator()

        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

    def create_msp(self):
        if self.msp_holder.check():
            self.logger.info("Msp files already exists: %s" % self.msp_holder.org_crypto_dir)
            self.msp_generator.extend(self)
            return
        self.msp_generator.generate(self)
