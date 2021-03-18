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
from config import env

SUPPORTED_DAEMON_TYPES = ["nodaemon", "supervisor", "launchd"]
DAEMON_CONFIG_SCRIPT = os.path.join(env.PROJECT_HOME, "scripts", "daemon-support", "config-daemon.sh")


class NodeProcessHandler:

    def __init__(self, target_dir, process_label):
        pass

    def boot_node(self):
        pass

    def stop_node(self):
        pass

    def check_node_process(self):
        pass

    def node_pid(self):
        pass

    def node_log_file(self):
        pass


def config_daemon(target_dir, process_label, command, daemon_type="nodaemon"):

    if daemon_type not in SUPPORTED_DAEMON_TYPES:
        raise Exception("Daemon type not support: %s" % daemon_type)

    if check_config(target_dir):
        return NodeProcessHandler(target_dir, process_label)

    result = subprocess.call([
        DAEMON_CONFIG_SCRIPT,
        "-d", daemon_type,
        "-n", process_label,
        "-h", target_dir,
        "-c", command
    ])
    if result != 0:
        raise Exception("Config daemon scripts error with code: %d" % result)
    return NodeProcessHandler(target_dir, process_label)


def check_config(target_dir):
    return os.path.exists(os.path.join(target_dir, "boot.sh")) and os.path.exists(os.path.join(target_dir, "stop.sh"))
