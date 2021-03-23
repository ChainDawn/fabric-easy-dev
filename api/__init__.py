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


class ApiConfig(dict):

    def __getattr__(self, item):
        return self[item]

    def __init__(self, org_map, **config):
        super(ApiConfig, self).__init__()
        self.update(config)
        self.Ord = org_map[self.Orderer["Org"]].node(self.Orderer["Name"])
        self.Prs = [org_map[p["Org"]].node(p["Name"]) for p in self.Peers]


class PeerNodeApi(metaclass=ABCMeta):

    @abstractmethod
    def joined_channels(self):
        pass

    @abstractmethod
    def installed_chaincode(self):
        pass

    @abstractmethod
    def install_chaincode(self):
        pass


class OrdererNodeApi(metaclass=ABCMeta):

    @abstractmethod
    def broadcast(self):
        pass


class ChannelApi(metaclass=ABCMeta):

    @abstractmethod
    def create(self, api_config, tx):
        pass

    @abstractmethod
    def update(self, tx):
        pass


class ChaincodeLifecycleApi(metaclass=ABCMeta):

    @abstractmethod
    def approve(self):
        pass

    @abstractmethod
    def commit(self):
        pass
