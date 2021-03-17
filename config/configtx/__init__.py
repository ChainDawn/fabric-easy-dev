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
from config.configtx.policy import Policy


def __channel_capabilities__():
    return {
        "V2.0": "true"
    }


def __channel_policies__():
    return {
        "Readers":              Policy("ImplicitMeta", "ANY Readers"),
        "Writers":              Policy("ImplicitMeta", "ANY Writers"),
        "Admins":               Policy("ImplicitMeta", "MAJORITY Admins"),
    }


class SystemChannelProfile(yaml.YAMLObject):

    def __init__(self, application, orderer, consortiums):
        self.Application = application
        self.Capabilities = __channel_capabilities__()
        self.Consortiums = consortiums
        self.Orderer = orderer
        self.Policies = __channel_policies__()


class ApplicationProfile(yaml.YAMLObject):

    def __init__(self, application, consortium):
        self.Application = application
        self.Capabilities = __channel_capabilities__()
        self.Consortium = consortium
        self.Policies = __channel_policies__()


class Profiles(yaml.YAMLObject):

    def __init__(self, **profile):
        self.Profiles = profile

    def __dump__(self):
        pass

    def generateSystemGenesisBlock(self, profile_name, sys_channel_name, target_dir):
        pass

    def generateCreateChannelTx(self, profile_name, channel_name, target_dir):
        pass
