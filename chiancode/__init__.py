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
KEY_USER_CHAINCODES = "UserChaincodes"


class UserChaincode(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, name, values):
        super().__init__()
        self.Name = name
        self.update(values)


def config_chaincodes(raw_conf):
    return {cc_name: UserChaincode(cc_name, raw_conf[cc_name])
            for cc_name in raw_conf.keys()}
