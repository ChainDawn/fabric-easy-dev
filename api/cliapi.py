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
from abc import ABC

import api
import os
import subprocess
import yaml
import env

from utils.fileutil import mkdir_if_need


def __dump_cli_core_conf__(target_dir, mspid, template=env.CLI_CORE_YAML_TEMPLATE):
    if not os.path.exists(template):
        raise ValueError("Cli core.yaml template file not exists: %s" % template)
    with open(template, "r") as template:
        template_yaml_data = yaml.load(template, yaml.CLoader)
    template_yaml_data["peer"]["localMspId"] = mspid
    with open(os.path.join(target_dir, "core.yaml"), "w") as target_file:
        yaml.dump(template_yaml_data, target_file)


class CliApiSupport(api.ApiSupport, ABC):

    def __init__(self, singer, cache_dir, peer_binary=env.PEER):
        if not os.path.exists(peer_binary):
            raise Exception("Peer binary not found: %s" % peer_binary)

        self.Signer = singer

        self.Dir = os.path.join(cache_dir, "cli-api-support")
        mkdir_if_need(self.Dir)

        self.Peer = os.path.join(self.Dir, "peer")
        os.system("cp %s %s" % (peer_binary, self.Peer))

        self.signer_dir = os.path.join(self.Dir, self.Signer.MspId, self.Signer.Name)

        mkdir_if_need(self.signer_dir)

        __dump_cli_core_conf__(self.signer_dir, self.Signer.MspId)
        os.system("cp -r %s/* %s" % (self.Signer.Dir, self.signer_dir))

    def channel(self, channel, orderer):
        return CliChannelApi(self, channel, orderer)

    def chaincode_lifecycle(self, chaincode, peer, orderer=None):
        return CliChaincodeLifecycleApi(self, chaincode, peer, orderer)

    def chaincode(self, chaincode, ch_name, peer, orderer=None):
        return CliChaincodeApi(self, chaincode, ch_name, peer, orderer)

    def peer(self, peer):
        return CliPeerApi(self, peer)

    def __execute_api__(self, args, orderer=None, envs=None):
        if orderer is not None:
            common_orderer_args = [
                "--orderer", orderer.deploy_handler.Address,
                "--tls",
                "--cafile", orderer.msp_holder.tls_ca(),
            ]
            args += common_orderer_args
        sub_env = {"FABRIC_CFG_PATH": self.signer_dir}
        if envs is not None:
            sub_env = {**envs, **sub_env}
        return subprocess.run([self.Peer, *args], env=sub_env)

    def __execute_api_join_env__(self, args, orderer=None, envs=None):
        if orderer is not None:
            common_orderer_args = [
                "--orderer", orderer.deploy_handler.Address,
                "--tls",
                "--cafile", orderer.msp_holder.tls_ca(),
            ]
            args += common_orderer_args
        os.putenv("FABRIC_CFG_PATH", self.signer_dir)
        for e_key in envs:
            os.putenv(e_key, envs[e_key])
        return subprocess.run([self.Peer, *args])


class CliChannelApi(api.ChannelApi, ABC):

    def __init__(self, support, channel, orderer):
        super(CliChannelApi, self).__init__()
        self.api = support
        self.channel = channel
        self.orderer = orderer

    def __execute__(self, cmd, args, peer=None):
        envs = None
        if peer is not None:
            envs = {"CORE_PEER_ADDRESS": peer.deploy_handler.Address}
        self.api.__execute_api__(["channel", cmd, *args], orderer=self.orderer, envs=envs)

    def create(self, tx):
        block_file = os.path.join(self.api.Dir, "%s.block" % self.channel.Name)
        self.__execute__("create", [
            "--channelID", self.channel.Name,
            "--file", tx,
            "--outputBlock", block_file,
        ])

    def update(self, tx):
        pass

    def fetch(self, fetch_type="oldest"):
        block_file = os.path.join(self.api.Dir, "%s-%s.block" % (self.channel.Name, fetch_type))
        self.__execute__("fetch", [
            fetch_type,
            block_file,
            "--channelID", self.channel.Name,
        ])
        return block_file

    def join(self, peer):
        latest_block_file = self.fetch()
        self.__execute__("join", [
            "-b", latest_block_file,
        ], peer)


class CliChaincodeLifecycleApi(api.ChaincodeLifecycleApi, ABC):

    def __init__(self, support, chaincode, peer, orderer):
        super(CliChaincodeLifecycleApi, self).__init__()
        self.api = support
        self.cc = chaincode
        self.peer = peer
        self.orderer = orderer

    def __execute_api__(self, cmd, params):
        return self.__execute__(cmd, params, func=self.api.__execute_api__)

    def __execute__(self, cmd, params, func):
        envs = {"CORE_PEER_ADDRESS": self.peer.deploy_handler.Address}
        return func(["lifecycle", "chaincode", cmd, *params], orderer=self.orderer, envs=envs)

    def get_installed_package(self, cache_dir):
        pass

    def approve(self, ch_name, package_id):
        self.__execute_api__("approveformyorg", [
            "--channelID", ch_name,
            "--name", self.cc.Name,
            "--version", str(self.cc.Version),
            "--package-id", package_id,
            "--sequence", str(self.cc.Sequence),
        ])

    def query_approved(self, ch_name):
        self.__execute_api__("queryapproved", [
            "-C", ch_name,
            "-n", self.cc.Name,
            "--sequence", str(self.cc.Sequence),
            "--output", "json",
        ])

    def commit(self, ch_name, endorsers=None):
        endorsers_params = []
        if endorsers is not None:
            for endorser in endorsers:
                endorsers_params += [
                    "--peerAddresses", endorser.deploy_handler.Address,
                    "--tlsRootCertFiles", endorser.msp_holder.tls_ca(),
                ]
        self.__execute_api__("commit", [
            "--channelID", ch_name,
            "--name", self.cc.Name,
            "--sequence", str(self.cc.Sequence),
            "--version", str(self.cc.Version),
        ] + endorsers_params)

    def query_committed(self, ch_name):
        self.__execute_api__("querycommitted", [
            "--channelID", ch_name,
            "--name", self.cc.Name,
        ])

    def check_commit_readiness(self, ch_name):
        self.__execute_api__("checkcommitreadiness", [
            "--channelID", ch_name,
            "--name", self.cc.Name,
            "--sequence", str(self.cc.Sequence),
            "--version", str(self.cc.Version),
            "--output", "json"
        ])


class CliPeerApi(api.PeerApi, ABC):

    def __init__(self, support, peer):
        self.api = support
        self.peer = peer

    def __execute__(self, args):
        return self.api.__execute_api__(args, envs={"CORE_PEER_ADDRESS": self.peer.deploy_handler.Address})

    def __execute_join_env__(self, args):
        return self.api.__execute_api_join_env__(args, envs={"CORE_PEER_ADDRESS": self.peer.deploy_handler.Address})

    def list_channels(self):
        self.api.__execute_api__([
            "channel", "list"
        ])

    def list_installed_chaincodes(self):
        self.api.__execute_api__([
            "lifecycle", "chaincode", "queryinstalled"
        ])

    def install_chaincode(self, chaincode):
        cc_pack = self.package_chaincode(chaincode)
        self.__execute__(["lifecycle", "chaincode", "install", cc_pack])

    def package_chaincode(self, cc):
        label = "%s.%s" % (cc.Name, cc.Version)
        target_package = os.path.join(self.api.Dir, "%s.tar.gz" % label)
        self.__execute_join_env__([
            "lifecycle", "chaincode", "package", target_package,
            "--path", cc.Path,
            "--lang", cc.Language,
            "--label", label])
        return target_package


class CliChaincodeApi(api.ChaincodeApi, ABC):

    def __init__(self, support, cc, ch_name, peer, orderer=None):
        self.cc = cc
        self.ch_name = ch_name
        self.api = support
        self.peer = peer
        self.orderer = orderer

    def __execute_api__(self, cmd, params):
        envs = {"CORE_PEER_ADDRESS": self.peer.deploy_handler.Address}
        return self.api.__execute_api__(["chaincode", cmd, *params], orderer=self.orderer, envs=envs)

    def invoke(self, params, endorsers):
        endorsers_params = []
        if endorsers is not None:
            for endorser in endorsers:
                endorsers_params += [
                    "--peerAddresses", endorser.deploy_handler.Address,
                    "--tlsRootCertFiles", endorser.msp_holder.tls_ca(),
                ]
        self.__execute_api__("invoke", [
            "-n", self.cc.Name,
            "-C", self.ch_name,
            "-c", params
        ] + endorsers_params)

    def query(self, params):
        pass
