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


class CryptoConfig(yaml.YAMLObject):
    yaml_tag = "!Crypto-config"

    def __init__(self, cryptogen=env.CRYPTOGEN):
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
