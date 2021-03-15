#!/usr/bin/python
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
import subprocess

from config.env import PLATFORM, FABRIC_VERSION, CACHE_DIR, FABRIC_BIN_DIR


def wget(source_url, cache_dir=CACHE_DIR):
    target_file = "%s/%s" % (cache_dir, os.path.basename(source_url))
    if os.path.exists(target_file):
        print("Target file already downloaded: %s" % target_file)
        return target_file
    if subprocess.call(["wget", "-P", cache_dir, source_url]) == 0:
        print("Target file download success: %s" % target_file)
        return target_file
    return None


def download_fabric_release_binaries(cache_dir=CACHE_DIR, target_dir=FABRIC_BIN_DIR):
    arch = PLATFORM + "-amd64"
    source_file = "hyperledger-fabric-%s-%s.tar.gz" % (arch, FABRIC_VERSION)
    download_url = "https://github.com/hyperledger/fabric/releases/download/v%s/%s" % (FABRIC_VERSION, source_file)

    binaries_tar_file = wget(download_url, cache_dir)
    if binaries_tar_file is None:
        print("Fabric binaries download failed: %s" % download_url)

    if not os.path.exists(target_dir):
        subprocess.call(["mkdir", "-p", target_dir])
    subprocess.call(["tar", "-zxvf", binaries_tar_file, "-C", target_dir])


def setup():
    if subprocess.call(["pip", "install", "-r", "requirements.txt"]) != 0:
        return
    download_fabric_release_binaries()


if __name__ == '__main__':
    setup()
