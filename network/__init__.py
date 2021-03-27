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
from channel import config_sys_channel, config_user_channel


class Network:

    def __init__(self, orgs_config, sys_channel_config, target_dir):
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

    def create_channel(self, config_file, channel_name):
        channel = config_user_channel(self.orgs_map, config_file, channel_name)
        channel.create_tx(self.channel_cache_dir)
