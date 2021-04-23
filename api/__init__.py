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

API_KEY_ORDERER = "Orderer"
API_KEY_ENDORSERS = "Endorsers"
API_KEY_COMMITTER = "Committers"
API_KEY_SIGNER = "Signer"


class ApiSupport(metaclass=ABCMeta):

    @abstractmethod
    def channel(self, channel, orderer):
        pass

    @abstractmethod
    def chaincode_lifecycle(self, chaincode, peer, orderer=None):
        pass

    @abstractmethod
    def chaincode(self, chaincode, peers, orderer=None):
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

    @abstractmethod
    def join(self, peer):
        pass

    @abstractmethod
    def list(self, peer):
        pass

    @abstractmethod
    def approve(self, peer, chaincode, package_id):
        pass


class PeerApi(metaclass=ABCMeta):

    @abstractmethod
    def channel_list(self):
        pass

    @abstractmethod
    def chaincode_installed(self):
        pass

    @abstractmethod
    def chaincode_install(self, chaincode):
        pass


class ChaincodeLifecycleApi(metaclass=ABCMeta):

    @abstractmethod
    def query_installed(self):
        pass

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def query_approved(self):
        pass

    @abstractmethod
    def approve(self):
        pass

    @abstractmethod
    def query_committed(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def check_commit_readiness(self):
        pass

    @abstractmethod
    def package(self, cache_dir):
        pass

    @abstractmethod
    def get_installed_package(self, cache_dir):
        pass


class ChaincodeApi(metaclass=ABCMeta):

    @abstractmethod
    def invoke(self, params, peers, orderer):
        pass

    @abstractmethod
    def query(self, params, peer):
        pass
