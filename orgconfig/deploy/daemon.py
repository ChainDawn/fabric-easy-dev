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
import env

SUPPORTED_DAEMON_TYPES = ["nodaemon", "supervisor", "launchd"]
DAEMON_CONFIG_SCRIPT = os.path.join(env.PROJECT_HOME, "scripts", "daemon-support", "config-daemon.sh")


class NodeProcessHandler:

    def __init__(self, node_dir, process_label):
        if not os.path.exists(node_dir):
            raise ValueError("Node directory not exists: %s" % node_dir)
        self.node_dir = node_dir
        self.process_label = process_label
        self.node_boot_script = os.path.join(self.node_dir, "boot.sh")
        if not os.path.exists(self.node_boot_script):
            raise ValueError("Node boot script not exist: %s" % self.node_boot_script)
        self.node_stop_script = os.path.join(self.node_dir, "stop.sh")
        if not os.path.exists(self.node_stop_script):
            raise ValueError("Node stop script not exist: %s" % self.node_stop_script)
        self.node_log_file = os.path.join(self.node_dir, "%s.log" % process_label)
        self.node_pid_file = os.path.join(self.node_dir, "pid")
        self.node_started = False
        if os.path.exists(self.node_pid_file) and \
                os.system("ps -ef | grep $(cat %s)" % self.node_pid_file) == 0:
            self.node_started = True

    def boot_node(self):
        if self.node_started:
            return
        print("starting peer: %s" % self.process_label)
        self.node_started = subprocess.call([self.node_boot_script]) == 0

    def stop_node(self):
        if not self.node_started:
            return
        print("stopping peer: %s" % self.process_label)
        self.node_started = not subprocess.call([self.node_stop_script]) == 0


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
