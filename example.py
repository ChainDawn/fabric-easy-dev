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
import env
import logging
from network import Network

import coloredlogs
coloredlogs.install(level='INFO')
logger = logging.getLogger("example")


if __name__ == '__main__':
    config_file = "./example-network.yaml"
    network_target_directory = os.path.join(env.TARGET_DIR, "example")

    logger.info("Start config fabric network")
    logger.debug("\tFabric version: v%s" % env.FABRIC_VERSION)
    logger.debug("\tNetwork organizations config file: %s" % config_file)
    logger.debug("\tNetwork system channel config file: %s" % config_file)
    logger.debug("\tNetwork config target directory: %s" % network_target_directory)

    network = Network(orgs_config=config_file, sys_channel_config=config_file, target_dir=network_target_directory)
    network.deploy()
