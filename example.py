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
import sys
import env
import logging
from network import Network

import coloredlogs
coloredlogs.DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
coloredlogs.DEFAULT_DATE_FORMAT = "%m-%d %H:%M:%S"
coloredlogs.install(level='INFO')
logger = logging.getLogger("example")


def usage():
    print("""
You should execute this script as:
    python example.py [sub_command]
    sub_command list:
        - deploy
        - boot
        - stop
        - up
        - down
    """)
    sys.exit(-1)


def execute_network(method, config_file="./example-network.yaml", target_dir=os.path.join(env.TARGET_DIR, "example")):
    logger.debug("Start config fabric network")
    logger.debug("\tFabric version: v%s" % env.FABRIC_VERSION)
    logger.debug("\tNetwork organizations config file: %s" % config_file)
    logger.debug("\tNetwork system channel config file: %s" % config_file)
    logger.debug("\tNetwork config target directory: %s" % target_dir)

    network = Network(config_file=config_file, target_dir=target_dir)
    Network.__dict__[method](network, *sys.argv[2:])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    sub_command = sys.argv[1]

    if not hasattr(Network, sub_command) or not callable(Network.__dict__[sub_command]):
        usage()

    execute_network(sub_command)
