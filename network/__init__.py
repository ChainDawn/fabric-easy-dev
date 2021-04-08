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
from orgconfig import config_organizations, find_node
from channel import config_sys_channel, config_user_channels
from api import support as api_support


class Network:

    def __init__(self, orgs_config, sys_channel_config, channels_config, target_dir):
        self.Dir = target_dir
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        self.orgs_map = config_organizations(orgs_config, target_dir)
        self.sys_channel = config_sys_channel(self.orgs_map, sys_channel_config)

        self.sys_channel_cache_dir = os.path.join(target_dir, self.sys_channel.Name)
        if not os.path.exists(self.sys_channel_cache_dir):
            os.system("mkdir -p %s" % self.sys_channel_cache_dir)

        self.channel_cache_dir = os.path.join(target_dir, "channels")
        if not os.path.exists(self.channel_cache_dir):
            os.system("mkdir -p %s" % self.channel_cache_dir)

        self.channels = config_user_channels(self.orgs_map, channels_config)

        self.api_cache_dir = os.path.join(target_dir, "api")
        if not os.path.exists(self.api_cache_dir):
            os.system("mkdir -p %s" % self.api_cache_dir)

    def echo_hosts(self, ip="127.0.0.1"):
        hosts_cache = ""
        for org in self.orgs_map.values():
            hosts_cache += "\n"
            hosts_cache += "# fabric network host configs for organization: %s\n" % org.Name
            for p in org.PeerNodes.values():
                hosts_cache += "%s\t%s\n" % (ip, p.Domain)
            for o in org.OrdererNodes.values():
                hosts_cache += "%s\t%s\n" % (ip, o.Domain)
        print(hosts_cache)

    def deploy(self):
        self.sys_channel.deploy(self.sys_channel_cache_dir)

    def boot(self):
        self.sys_channel.boot()

    def stop(self):
        self.sys_channel.stop()

    def clear(self):
        self.sys_channel.clear()

    def up(self):
        self.sys_channel.deploy(self.sys_channel_cache_dir)
        self.sys_channel.boot()

    def down(self):
        self.clear()
        os.system("rm -fr %s" % self.Dir)

    def status(self, node_name=None):
        if node_name is None:
            self.sys_channel.status()
        else:
            node = find_node(self.orgs_map, node_name)
            node.deploy_handler.display()

    def __channel_cache_dir__(self, ch_name):
        return os.path.join(self.channel_cache_dir, ch_name)

    def __channel__(self, ch_name):
        if ch_name not in self.channels:
            raise Exception("No channel configuration found: %s" % ch_name)
        return self.channels[ch_name]

    def channel_create(self, ch_name, orderer_name):
        orderer = find_node(self.orgs_map, orderer_name)
        support = api_support.cli_api_support(orderer.Org.admin(), self.__channel_cache_dir__(ch_name))
        self.__channel__(ch_name).create(support, orderer)

    def channel_join(self, ch_name, peer_name, orderer_name):
        peer = find_node(self.orgs_map, peer_name)
        orderer = find_node(self.orgs_map, orderer_name)
        support = api_support.cli_api_support(peer.Org.admin(), self.__channel_cache_dir__(ch_name))
        self.__channel__(ch_name).join(support, peer, orderer)

    def channel_list(self, peer_name):
        peer = find_node(self.orgs_map, peer_name)
        support = api_support.cli_api_support(peer.Org.admin(), self.api_cache_dir)
        support.peer(peer.deploy_handler.Address).channel_list()

    def chaincode_list_installed(self, peer_name):
        peer = find_node(self.orgs_map, peer_name)
        support = api_support.cli_api_support(peer.Org.admin(), self.api_cache_dir)
        support.peer(peer.deploy_handler.Address).chaincode_installed()
