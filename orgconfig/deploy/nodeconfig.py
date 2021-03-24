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
import os
import env


def config_core_yaml(deploy_handler, template_file=env.CORE_YAML_TEMPLATE):
    with open(template_file, 'r') as template:
        core_yaml_data = yaml.load(template, yaml.CLoader)

    # modify
    core_yaml_data["peer"]["listenAddress"] = deploy_handler.ListenAddress
    core_yaml_data["peer"]["address"] = deploy_handler.ListenAddress
    core_yaml_data["peer"]["chaincodeListenAddress"] = deploy_handler.ChaincodeListenAddress
    core_yaml_data["peer"]["gossip"]["bootstrap"] = deploy_handler.gossip_bootstrap_address()
    core_yaml_data["peer"]["localMspId"] = deploy_handler.Node.Org.MSPID
    core_yaml_data["operations"]["listenAddress"] = deploy_handler.OperationsListenAddress

    # dump into target directory.
    with open(os.path.join(deploy_handler.Dir, "core.yaml"), 'w') as target_file:
        yaml.dump(core_yaml_data, target_file)


def config_orderer_yaml(deploy_handler, template_file=env.ORDERER_YAML_TEMPLATE):
    with open(template_file, 'r') as template:
        orderer_yaml_data = yaml.load(template, yaml.CLoader)

    orderer_yaml_data["General"]["ListenPort"] = deploy_handler.ListenPort
    orderer_yaml_data["General"]["LocalMSPID"] = deploy_handler.Node.Org.MSPID
    orderer_yaml_data["Operations"]["ListenAddress"] = deploy_handler.OperationsListenAddress

    # dump into target directory.
    target_file_path = os.path.join(deploy_handler.Dir, "orderer.yaml")
    with open(target_file_path, 'w') as target_file:
        yaml.dump(orderer_yaml_data, target_file)
