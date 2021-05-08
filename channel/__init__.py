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
from channel.configtx import ConfigTxSupport
from orgconfig import find_node, find_user
from api import support as api_support

import os

KEY_SYS_CHANNEL = "SystemChannel"
KEY_USER_CHANNELS = "UserChannels"


def __default_tx_support__():
    return ConfigTxSupport()


class SystemChannel(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, orgs_map, **config):
        super(SystemChannel, self).__init__()
        self.update(config)

        self.Orgs = [orgs_map[name] for name in self.Organizations]
        self.Ords = [find_node(orgs_map, orderer) for orderer in self.Orderers]

    def genesis(self, cache_dir, tx_support=__default_tx_support__()):
        return tx_support.generate_syschannel_genesis_block(self, cache_dir)

    def deploy(self, cache_dir):
        genesis_block_file = self.genesis(cache_dir)
        for org in self.Orgs:
            org.deploy_peers()
        for ord in self.Ords:
            ord.deploy_handler.deploy(genesis_block_file)

    def boot(self):
        self.__call_on_all_nodes__(lambda n: n.deploy_handler.proc_handler.boot())

    def stop(self):
        self.__call_on_all_nodes__(lambda n: n.deploy_handler.proc_handler.stop())

    def clear(self):
        self.__call_on_all_nodes__(lambda n: n.deploy_handler.clear())

    def status(self):
        self.__call_on_all_nodes__(lambda n: n.deploy_handler.display())

    def __call_on_all_nodes__(self, _callback):
        for org in self.Orgs:
            for node in org.PeerNodes.values():
                _callback(node)
        for ord in self.Ords:
            _callback(ord)


class UserChannel(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, orgs_map, channel_name, cache_dir, **config):
        super(UserChannel, self).__init__()
        self.update(config)
        self.Name = channel_name
        self.Orgs = {name: orgs_map[name] for name in self.Organizations}
        self.orgs_map = orgs_map
        self.cache_dir = os.path.join(cache_dir, self.Name)

    def __create_tx__(self, tx_support=__default_tx_support__()):
        return tx_support.generate_create_channel_tx(self, self.cache_dir)

    def update_tx(self, tx):
        pass

    def create(self, orderer_name):
        orderer = self.__get_node__(orderer_name)
        support = api_support.cli_api_support(orderer.Org.admin(), self.cache_dir)
        ch_api = support.channel(self, orderer)
        tx = self.__create_tx__()
        return ch_api.create(tx)

    def join(self, orderer_name, peer_name):
        orderer = self.__get_node__(orderer_name)
        peer = self.__get_node__(peer_name)
        support = api_support.cli_api_support(peer.Org.admin(), self.cache_dir)
        ch_api = support.channel(self, orderer)
        return ch_api.join(peer)

    def __get_node__(self, name):
        return find_node(self.orgs_map, name)


def config_sys_channel(orgs_map, raw_conf):
    return SystemChannel(orgs_map, **raw_conf)


def config_user_channels(orgs_map, cache_dir, raw_conf):
    return {ch_name: UserChannel(orgs_map, ch_name, cache_dir, **raw_conf[ch_name])
            for ch_name in raw_conf.keys()}
