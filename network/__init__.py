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
from orgconfig import config_organizations
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
        pass

    def status(self):
        self.sys_channel.status()

    def __channel_cache_dir__(self, ch_name):
        return os.path.join(self.channel_cache_dir, ch_name)

    def __channel__(self, ch_name):
        if ch_name not in self.channels:
            raise Exception("No channel configuration found: %s" % ch_name)
        return self.channels[ch_name]

    def create_channel(self, ch_name, api_config_file):
        support = api_support.cli_api_support(self.orgs_map, api_config_file, self.__channel_cache_dir__(ch_name))
        self.__channel__(ch_name).create(support)

    def join_channel(self, ch_name, peer, api_config_file):
        ps = str(peer).split(".")
        if len(ps) != 2:
            raise ValueError("Peer node error: %s, correct format is: org_name.node_name, example: Org1.peer0" % ps)
        support = api_support.cli_api_support(self.orgs_map, api_config_file, self.__channel_cache_dir__(ch_name))
        self.__channel__(ch_name).join(support, ps[0], ps[1])

