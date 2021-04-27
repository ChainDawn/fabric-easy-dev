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
    def chaincode(self, chaincode, ch_name, peers, orderer=None):
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


class ChaincodeLifecycleApi(metaclass=ABCMeta):

    @abstractmethod
    def query_approved(self, ch_name):
        pass

    @abstractmethod
    def approve(self, ch_name, package_id):
        pass

    @abstractmethod
    def query_committed(self, ch_name):
        pass

    @abstractmethod
    def commit(self, cc_name, endorsers=None):
        pass

    @abstractmethod
    def check_commit_readiness(self, ch_name):
        pass

    @abstractmethod
    def get_installed_package(self, cache_dir):
        pass


class ChaincodeApi(metaclass=ABCMeta):

    @abstractmethod
    def invoke(self, params, peers):
        pass

    @abstractmethod
    def query(self, params):
        pass


class PeerApi(metaclass=ABCMeta):

    @abstractmethod
    def list_channels(self):
        pass

    @abstractmethod
    def list_installed_chaincodes(self):
        pass

    @abstractmethod
    def package_chaincode(self, chaincode):
        pass

    @abstractmethod
    def install_chaincode(self, chaincode):
        pass
