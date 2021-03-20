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
import yaml
from config.configtx.policy import Policy


def __capabilities__():
    return {
        "V2.0": "true"
    }


def __policies__():
    return {
        "Readers":              Policy("ImplicitMeta", "ANY Readers"),
        "Writers":              Policy("ImplicitMeta", "ANY Writers"),
        "Admins":               Policy("ImplicitMeta", "MAJORITY Admins"),
        "BlockValidation":      Policy("ImplicitMeta", "ANY Writers"),
    }


class Consenter(yaml.YAMLObject):

    def __init__(self, orderer_node):
        self.Host = orderer_node.Domain
        self.Port = orderer_node.ListenPort
        self.ServerTLSCert = orderer_node.server_tls_cert()
        self.ClientTLSCert = orderer_node.server_tls_cert()


class EtcdRaft(yaml.YAMLObject):

    def __init__(self, consenters):
        self.Consenters = consenters
        self.Options = {
            "TickInterval":         "500ms",
            "ElectionTick":         "10",
            "HeartbeatTick":        "1",
            "MaxInflightBlocks":    "1",
            "SnapshotIntervalSize": "16 MB",
        }


class Orderer(yaml.YAMLObject):

    def __init__(self, etcdraft, addresses, channel_orgs):
        self.OrdererType = "etcdraft"
        self.Addresses = addresses
        self.BatchTimeout = "2s"
        self.BatchSize = {
            "MaxMessageCount": "500",
            "AbsoluteMaxBytes": "10 MB",
            "PreferredMaxBytes": "2 MB",
        }
        self.MaxChannels = 0
        self.EtcdRaft = etcdraft
        self.Organizations = channel_orgs
        self.Capabilities = __capabilities__()
        self.Policies = __policies__()
