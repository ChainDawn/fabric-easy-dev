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


def __default_tx_support__():
    return ConfigTxSupport()


class SystemChannel(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, orgs_map, **config):
        super(SystemChannel, self).__init__()
        self.update(config)

        self.Orgs = [orgs_map[name] for name in self.Organizations]
        self.Ords = [orgs_map[org_name].NodeMap[node_name]
                     for ordorgs in self.Orderers
                     for org_name in ordorgs
                     for node_name in ordorgs[org_name]]

    def genesis(self, cache_dir, tx_support=__default_tx_support__()):
        return tx_support.generate_syschannel_genesis_block(self, cache_dir)


class UserChannel(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, orgs_map, **config):
        super(UserChannel, self).__init__()
        self.update(config)
        self.Orgs = [orgs_map[name] for name in self.Organizations]

    def create_tx(self, cache_dir, tx_support=__default_tx_support__()):
        return tx_support.generate_create_channel_tx(self, cache_dir)
