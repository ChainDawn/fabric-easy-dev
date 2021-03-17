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
import yaml


class ConfigGenerator:

    def __init__(self, template):
        if not os.path.exists(template):
            raise ValueError("Template file not exists: %s" % template)
        self.template = template

    def generate(self, node, target_dir, gossip_bootstrap):
        with open(self.template, 'r') as template:
            core_yaml_data = yaml.load(template, yaml.CLoader)
        # modify
        core_yaml_data["peer"]["listenAddress"] = node.ListenAddress
        core_yaml_data["peer"]["address"] = node.ListenAddress
        core_yaml_data["peer"]["chaincodeListenAddress"] = node.ChaincodeListenAddress
        core_yaml_data["peer"]["gossip"]["bootstrap"] = gossip_bootstrap
        core_yaml_data["peer"]["localMspId"] = node.MSPID
        core_yaml_data["operations"]["listenAddress"] = node.OperationsListenAddress
        # dump into target directory.
        target_file_path = os.path.join(target_dir, "core.yaml")
        with open(os.path.join(target_dir, "core.yaml"), 'w') as target_file:
            yaml.dump(core_yaml_data, target_file)
        return target_file_path
