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
import logging
import env

SUPPORTED_DAEMON_TYPES = ["nodaemon", "supervisor", "launchd"]
DAEMON_CONFIG_SCRIPT = os.path.join(env.PROJECT_HOME, "scripts", "daemon-support", "config-daemon.sh")


class DaemonProcessHandler:

    def __init__(self, p_dir, p_label, command, daemon_type="nodaemon", re_config=False):
        self.Dir = p_dir
        self.Label = p_label
        self.daemon_type = daemon_type
        self.boot_script = os.path.join(self.Dir, "boot.sh")
        self.stop_script = os.path.join(self.Dir, "stop.sh")
        self.log_file = os.path.join(self.Dir, "%s.log" % self.Label)
        self.pid_file = os.path.join(self.Dir, "pid")
        self.logger = logging.getLogger("Process")

        if not re_config and self.__bootable__() and self.__stoppable__():
            self.logger.info("Scripts for process [%s] already exists. No need to re-generate." % p_label)
            return

        if not os.path.exists(self.Dir):
            raise ValueError("Node directory not exists: %s" % self.Dir)

        if daemon_type not in SUPPORTED_DAEMON_TYPES:
            raise ValueError("Daemon type not support: %s" % daemon_type)

        subprocess.call([DAEMON_CONFIG_SCRIPT,
                         "-d", daemon_type, "-n", self.Label, "-h", self.Dir, "-c", command])

        if not os.path.exists(self.boot_script):
            raise ValueError("Node boot script not exist: %s" % self.boot_script)
        if not os.path.exists(self.stop_script):
            raise ValueError("Node stop script not exist: %s" % self.stop_script)

    def boot(self):
        if self.check():
            self.logger.info("Process already started: %s" % self.Label)
            return
        if not self.__bootable__():
            raise Exception("Boot script may not exists: %s" % self.boot_script)
        self.logger.info("Starting process: %s" % self.Label)
        os.system(self.boot_script)

    def stop(self):
        if not self.check():
            self.logger.info("Process already stopped: %s" % self.Label)
            return
        if not self.__stoppable__():
            raise Exception("Stop script may not exists: %s" % self.stop_script)
        self.logger.info("Stopping process: %s" % self.Label)
        os.system(self.stop_script)

    def __bootable__(self):
        return os.path.exists(self.boot_script)

    def __stoppable__(self):
        return os.path.exists(self.stop_script)

    def check(self):
        if not os.path.exists(self.pid_file):
            return False
        if not os.system("ps -aux | grep $(cat %s) >> null" % self.pid_file) == 0:
            return False
        return True
