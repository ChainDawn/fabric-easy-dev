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


class BaseConfigModel(dict):

    def __getattr__(self, item):
        return self[item]


class Node(BaseConfigModel):

    def __init__(self, organization, **config):
        super().__init__()
        self.update(config)
        self.Org = organization

        self.Domain = "%s.%s" % (self.Name, self.Org.Domain)
        self.Address = "%s:%s" % (self.Domain, self.ListenPort)

        self.Dir = os.path.join(organization.Dir, self.Name)
        if not os.path.exists(self.Dir):
            subprocess.call(["mkdir", "-p", self.Dir])

        self.MspDir = os.path.join(self.Dir, "msp")
        if not os.path.exists(self.MspDir):
            node_msp_source = self.Org.node_msp(self.Name)
            if not os.path.exists(node_msp_source):
                raise Exception("Node msp directory not exists: %s" % node_msp_source)
            os.system("cp -r %s %s" % (node_msp_source, self.MspDir))

        self.TlsDir = os.path.join(self.Dir, "tls")
        if not os.path.exists(self.TlsDir):
            node_tls_source = self.Org.node_tls(self.Name)
            if not os.path.exists(node_tls_source):
                raise Exception("Node tls directory not exists: %s" % node_tls_source)
            os.system("cp -r %s %s" % (node_tls_source, self.TlsDir))

        if self.Type != "peer" and self.Type != "orderer":
            raise ValueError("Error node type: %s", self.Type)

    def gossip_bootstrap_address(self):
        return self.Org.node_access_address(self.GossipBootStrapNode)

    def process_label(self):
        return "%s-%s-%s" % (self.Org.Name, self.Type, self.Name)

    def config(self, bootstrap_config_generator):
        bootstrap_config_generator.config(self)

    def server_tls_cert(self):
        return self.Org.node_server_tls_cert(self.Name)


class Organization(BaseConfigModel):

    def __init__(self, target_dir, msp_support, **values):
        super().__init__()
        self.update(values)

        if not os.path.exists(target_dir):
            raise ValueError("target_dir not exists: %s" % target_dir)
        self.Dir = os.path.join(target_dir, self.Name)
        if not os.path.exists(self.Dir):
            subprocess.call(["mkdir", "-p", self.Dir])

        self.MspBaseDir = os.path.join(self.Dir, self.MSPID)
        self.msp_generator, self.msp_source_holder = msp_support(self)

        if not os.path.exists(self.MspBaseDir):
            self.msp_generator.generate(self)

        if not self.msp_source_holder.check():
            raise Exception("Organization msp check failed!!")

        if len(self.Nodes) == 0:
            # TODO log information.
            return

        self.NodeMap = {node["Name"]: Node(self, **node) for node in self.Nodes}

    def add_node(self, *nodes):
        pass

    def node_access_address(self, node_name):
        pass

    def node_msp(self, node_name):
        return self.msp_source_holder.node_msp(node_name)

    def node_tls(self, node_name):
        return self.msp_source_holder.node_tls(node_name)

    def node_server_tls_cert(self, node_name):
        return self.msp_source_holder.node_server_tls_cert(node_name)


class Config(BaseConfigModel):

    def __init__(self, **source):
        super().__init__()
        self.update(source)
        if "Organizations" in source:
            self.Organizations = [Organization(**item) for item in source["Organizations"]]

    def generate_msp(self, target_dir):
        for organization in self.Organizations:
            organization.build(target_dir)
