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

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import yaml
from config import env
from config.configtx.policy import Policy
from config.configtx.organization import Organization
from config.configtx.application import Application
from config.configtx.orderer import Orderer, EtcdRaft, Consenter


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

    def __init__(self, sys_channel):
        channel_orgs = [Organization(o.Name, o.MSPID, o.msp_dir()) for o in sys_channel.Orgs]
        self.Application = Application(channel_orgs)
        self.Capabilities = __channel_capabilities__()
        self.Consortiums = {"SimpleConsortiums": {"Organizations": channel_orgs}}
        etcdraft = EtcdRaft([Consenter(node) for node in sys_channel.Ords])
        addresses = [node.Address for node in sys_channel.Ords]
        self.Orderer = Orderer(etcdraft, addresses, channel_orgs)
        self.Policies = __channel_policies__()


class UserChannelProfile(yaml.YAMLObject):

    def __init__(self, _application, _consortium):
        self.Application = _application
        self.Capabilities = __channel_capabilities__()
        self.Consortium = _consortium
        self.Policies = __channel_policies__()


class Profiles(yaml.YAMLObject):

    def __init__(self, profiles):
        self.Profiles = profiles

    def dump(self, target_file):
        with open(target_file, "w") as config_file:
            yaml.dump(self, config_file)
        return target_file


class ConfigTxSupport:

    def __init__(self, configtxgen=env.CONFIGTXGEN):
        self.cmd = configtxgen

    def generate(self, channel, target_dir, is_sys=False):
        if not os.path.exists(target_dir):
            raise ValueError("Target directory not exists: %s" % target_dir)

        profile_name = "%s-Profile" % channel.Name
        profile = SystemChannelProfile(channel) if is_sys else UserChannelProfile(channel)
        profiles = Profiles({profile_name: profile})
        profiles.dump(os.path.join(target_dir, "configtx.yaml"))
        if is_sys:
            self.genesis_block(profile_name, channel.Name, target_dir, target_dir)
        else:
            self.channel_tx(profile_name, channel.Name, target_dir, target_dir)

    def genesis_block(self, profile_name, channel_name, config_dir, target_dir):
        import subprocess
        output = os.path.join(target_dir, "genesis.block")
        if subprocess.call([self.cmd,
                            "-profile", profile_name,
                            "-channelID", channel_name,
                            "-outputBlock", output,
                            "-configPath", config_dir]) == 0:
            return output

    def channel_tx(self, profile_name, channel_name, config_dir, target_dir):
        pass
