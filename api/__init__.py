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
from abc import ABCMeta, abstractmethod
from orgconfig import find_user, find_node

API_KEY_ORDERER = "Orderer"
API_KEY_ENDORSERS = "Endorsers"
API_KEY_COMMITTER = "Committers"
API_KEY_SIGNER = "Signer"


class ApiConfig:

    def __init__(self, org_map, **config):
        self.Signer = find_user(org_map, config[API_KEY_SIGNER])
        self.Orderer = find_node(org_map, config[API_KEY_ORDERER])
        if API_KEY_ENDORSERS in config:
            self.Endorsers = [find_node(org_map, peer) for peer in config[API_KEY_ENDORSERS]]
        if API_KEY_COMMITTER in config:
            self.Committers = [find_node(org_map, peer) for peer in config[API_KEY_COMMITTER]]


class ApiSupport(metaclass=ABCMeta):

    @abstractmethod
    def channel(self, channel):
        pass

    @abstractmethod
    def chaincode_lifecycle(self):
        pass

    @abstractmethod
    def chaincode(self):
        pass

    @abstractmethod
    def peer(self, peer):
        pass


class ChannelApi(metaclass=ABCMeta):

    @abstractmethod
    def create(self, tx):
        pass

    @abstractmethod
    def update(self, tx):
        pass

    def join(self, peers):
        pass


class PeerApi(metaclass=ABCMeta):

    @abstractmethod
    def channel_list(self):
        pass

    @abstractmethod
    def chaincode_installed(self):
        pass
