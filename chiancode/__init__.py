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
from api import support as api_support


KEY_USER_CHAINCODES = "UserChaincodes"


class UserChaincode(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, name, values):
        super().__init__()
        self.Name = name
        self.update(values)

    def approve(self, ch, peer_name, orderer_name, package_id):
        self.__cc_lc_api__(ch, peer_name, orderer_name).approve(ch.Name, package_id)

    def query_approve(self, ch, peer_name):
        self.__cc_lc_api__(ch, peer_name).query_approved(ch.Name)

    def check_commit_readiness(self, ch, peer_name):
        self.__cc_lc_api__(ch, peer_name).check_commit_readiness(ch.Name)

    def commit(self, ch, orderer_name, *endorser_names):
        if len(endorser_names) == 0:
            raise KeyError("Endorsers is empty")
        endosers = []
        for e_name in endorser_names:
            endosers.append(ch.__get_node__(e_name))
        self.__cc_lc_api__(ch, endorser_names[0], orderer_name).commit(ch.Name, endosers)

    def query_committed(self, ch, peer_name):
        self.__cc_lc_api__(ch, peer_name).query_committed(ch.Name)

    def __cc_lc_api__(self, ch, peer_name, orderer_name=None):
        peer = ch.__get_node__(peer_name)
        orderer = None
        if orderer_name is not None:
            orderer = ch.__get_node__(orderer_name)
        support = api_support.cli_api_support(peer.Org.admin(), ch.cache_dir)
        return support.chaincode_lifecycle(self, peer, orderer)

    def query(self, ch, peer_name, params):
        peer = ch.__get_node__(peer_name)
        support = api_support.cli_api_support(peer.Org.admin(), ch.cache_dir)
        cc_api = support.chaincode(self, ch.Name, peer)
        cc_api.query(params)

    def invoke(self, ch, orderer_name, *endorser_names, params):
        orderer = ch.__get_node__(orderer_name)
        endosers = []
        for e_name in endorser_names:
            endosers.append(ch.__get_node__(e_name))
        support = api_support.cli_api_support(endosers[0].Org.admin(), ch.cache_dir)
        cc_api = support.chaincode(self, ch.Name, endosers[0], orderer)
        cc_api.invoke(params, endosers)


def config_chaincodes(raw_conf):
    return {cc_name: UserChaincode(cc_name, raw_conf[cc_name])
            for cc_name in raw_conf.keys()}
