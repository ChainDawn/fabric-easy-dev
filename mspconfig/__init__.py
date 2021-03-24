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
import logging
import os
import yaml
from mspconfig.msp import static_msp_support


class Organization(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, target_dir, msp_support=static_msp_support, **values):
        super().__init__()
        self.update(values)

        self.logger = logging.getLogger("organization")

        self.Dir = os.path.join(target_dir, self.Name)
        if not os.path.exists(self.Dir):
            os.system("mkdir -p %s" % self.Dir)

        self.msp_support = msp_support(self)

        self.logger.info("Config organization: %s, mspid: %s" % (self.Name, self.MSPID))
        self.logger.debug("\tOrganization directory: %s" % self.Dir)

        self.msp_support.create_msp()


KEY_ORGANIZATIONS = "Organizations"


def config_organizations(config_file, target_dir):
    if not os.path.exists(config_file):
        raise ValueError("Config file not exists: %s" % config_file)
    with open(config_file, 'r') as conf:
        raw_conf = yaml.load(conf, yaml.CLoader)
    if KEY_ORGANIZATIONS not in raw_conf:
        raise Exception("No organization found in config file: %s" % config_file)
    return {org["Name"]: Organization(target_dir, **org) for org in raw_conf[KEY_ORGANIZATIONS]}
