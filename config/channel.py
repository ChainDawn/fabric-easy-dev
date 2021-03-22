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
import os, logging
from config.configtx import ConfigTxSupport


class SystemChannel(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, target_dir, orgs_map, **config):
        super(SystemChannel, self).__init__()
        self.update(config)

        self.Dir = os.path.join(target_dir, self.Name)
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        self.Orgs = [orgs_map[name] for name in self.Organizations]
        self.Ords = [orgs_map[org_name].NodeMap[node_name]
                     for ordorgs in self.Orderers
                     for org_name in ordorgs
                     for node_name in ordorgs[org_name]]

        self.GenesisBlock = os.path.join(self.Dir, "genesis.block")
        if not os.path.exists(self.GenesisBlock):
            tx_support = ConfigTxSupport()
            tx_support.generate_syschannel_genesis_block(self, self.Dir)


class UserChannel(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, target_dir, orgs_map, **config):
        super(UserChannel, self).__init__()
        self.update(config)
        self.logger = logging.getLogger("channel")

        self.logger.info("Config user channel: %s" % self.Name)

        self.Dir = os.path.join(target_dir, self.Name)
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        self.logger.debug("\tChannel directory: %s" % self.Dir)

        self.Orgs = [orgs_map[name] for name in self.Organizations]
        self.CreateTx = os.path.join(self.Dir, "%s.tx" % self.Name)
        if not os.path.exists(self.CreateTx):
            tx_support = ConfigTxSupport()
            self.CreateTx = tx_support.generate_create_channel_tx(self, self.Dir)

    def deploy(self):
        pass
