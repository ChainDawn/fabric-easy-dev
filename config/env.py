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
import platform

PLATFORM = str(platform.system()).lower()

PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FABRIC_VERSION = "2.2.0"

TARGET_DIR = os.path.join(PROJECT_HOME, "target")
CACHE_DIR = os.path.join(TARGET_DIR, "cache")

FABRIC_BIN_DIR = os.path.join(TARGET_DIR, "fabric-%s-v%s" % (PLATFORM, FABRIC_VERSION), "bin")

CRYPTOGEN = os.path.join(FABRIC_BIN_DIR, "cryptogen")
CONFIGTXGEN = os.path.join(FABRIC_BIN_DIR, "configtxgen")
PEER = os.path.join(FABRIC_BIN_DIR, "peer")
ORDERER = os.path.join(FABRIC_BIN_DIR, "orderer")

CORE_YAML_TEMPLATE = os.path.join(PROJECT_HOME, "templates", "core.yaml")
ORDERER_YAML_TEMPLATE = os.path.join(PROJECT_HOME, "templates", "orderer.yaml")
