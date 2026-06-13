# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------------------------------------------
#   Spawn — A fast and modern, open-source IDE with a native user interface for SA-MP and open.mp server development.
#   Copyright (C) 2026  Daniil Korochansky
#
#   This file is part of Spawn.
#
#   Spawn is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Spawn is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Spawn.  If not, see <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------------------------------------------------

import logging
import os
import sys
import platform

class SpawnLogger:
    _initialized = False

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        log_dir = os.path.join(
            os.environ["APPDATA"],
            "Spawn",
            "logs"
        )

        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(
            log_dir,
            "spawn.log"
        )

        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format=(
                "[%(asctime)s] "
                "%(levelname)s "
                "%(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8"
        )

        cls._initialized = True

    @staticmethod
    def info(message):
        logging.info(message)

    @staticmethod
    def warning(message):
        logging.warning(message)

    @staticmethod
    def error(message):
        logging.error(message)

    @staticmethod
    def exception(message):
        logging.exception(message)
        
    @staticmethod
    def generate_bug_report(spawn_version):
        log_dir = os.path.join(os.environ["APPDATA"],"Spawn","logs")
        log_file_path = os.path.join(log_dir,"spawn.log")
    
        report = []
        report.append("# Bug Report")
        report.append("")
        report.append(f"Spawn Version: {spawn_version}")
        report.append(f"Python Version: {sys.version}")
        report.append(f"Operating System: {platform.platform()}")
        report.append("")

        report.append("## Log Output")
        report.append("```")

        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()

                if lines:
                    report.extend([line.rstrip() for line in lines[-100:]])
                else:
                    report.append("No log entries found. Please describe the issue below.")
            except Exception as e:
                report.append(f"Failed to read log: {e}")
        else:
            report.append("Log file not found.")

        report.append("```")

        return "\n".join(report)
