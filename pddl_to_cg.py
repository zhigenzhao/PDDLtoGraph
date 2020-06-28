#! /usr/bin/env python3
#
# Copyright (C) 2020 Zhigen Zhao
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import sys
import os
import re
import logging
import networkx as nx
import pygraphviz as pgv

try:
    import argparse
except ImportError:
    from external import argparse

from pddl.parser import Parser
import tools

NUMBER = re.compile(r'\d+')

def validator_available():
    """
    unmodified pyperplan function
    """
    return tools.command_available(['validate', '-h'])



