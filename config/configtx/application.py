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


def __acls__():
    return {
        # _lifecycle
        "_lifecycle/CheckCommitReadiness":          "/Channel/Application/Writers",
        "_lifecycle/CommitChaincodeDefinition":     "/Channel/Application/Writers",
        "_lifecycle/QueryChaincodeDefinition":      "/Channel/Application/Readers",
        "_lifecycle/QueryChaincodeDefinitions":     "/Channel/Application/Readers",

        # lscc
        "lscc/ChaincodeExists":                     "/Channel/Application/Readers",
        "lscc/GetDeploymentSpec":                   "/Channel/Application/Readers",
        "lscc/GetChaincodeData":                    "/Channel/Application/Readers",
        "lscc/GetInstantiatedChaincodes":           "/Channel/Application/Readers",

        # qscc
        "qscc/GetChainInfo":                        "/Channel/Application/Readers",
        "qscc/GetBlockByNumber":                    "/Channel/Application/Readers",
        "qscc/GetBlockByHash":                      "/Channel/Application/Readers",
        "qscc/GetTransactionByID":                  "/Channel/Application/Readers",
        "qscc/GetBlockByTxID":                      "/Channel/Application/Readers",

        # cscc
        "cscc/GetConfigBlock":                      "/Channel/Application/Readers",
        "cscc/GetConfigTree":                       "/Channel/Application/Readers",
        "cscc/SimulateConfigTreeUpdate":            "/Channel/Application/Readers",

        # peer
        "peer/Propose":                             "/Channel/Application/Writers",
        "peer/ChaincodeToChaincode":                "/Channel/Application/Readers",

        # event
        "event/Block":                              "/Channel/Application/Readers",
        "event/FilteredBlock":                      "/Channel/Application/Readers",
    }


def __policies__():
    return {
        "Readers":              Policy("ImplicitMeta", "ANY Readers"),
        "Writers":              Policy("ImplicitMeta", "ANY Writers"),
        "Admins":               Policy("ImplicitMeta", "MAJORITY Admins"),
        "Endorsement":          Policy("ImplicitMeta", "MAJORITY Endorsement"),
        "LifecycleEndorsement": Policy("ImplicitMeta", "MAJORITY Endorsement"),
    }


class Application(yaml.YAMLObject):

    def __init__(self, organizations):
        self.ACLs = __acls__()
        self.Capabilities = __capabilities__()
        self.Organizations = organizations
        self.Policies = __policies__()
