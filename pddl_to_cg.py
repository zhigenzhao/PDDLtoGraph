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

class CGNodes(object):
    def CGNodes(self):
        pass

    def __eq__(self):
        return 0

    def __hash__(self):
        return 0

def validator_available():
    """
    unmodified pyperplan function
    """
    return tools.command_available(['validate', '-h'])

def parse(domain_file, problem_file):
    """ unmodified pyperplan function
    Args:
        domain_file: string domain filename
        problem_file: string problem filename
    Returns:
        problem: pddl.Problem object
    """

    parser = Parser(domain_file, problem_file)
    logging.info("Parsing Domain {0}".format(domain_file))
    domain = parser.parse_domain()
    logging.info('Parsing Problem {0}'.format(problem_file))
    problem = parser.parse_problem(domain)

    logging.debug(domain)
    logging.info('{0} Predicates parsed'.format(len(domain.predicates)))
    logging.info('{0} Actions parsed'.format(len(domain.actions)))
    logging.info('{0} Objects parsed'.format(len(problem.objects)))
    logging.info('{0} Constants parsed'.format(len(domain.constants)))

    return problem

def ground(problem):
    """
    unmodified pyperplan function
    """
    logging.info('Grounding start: {0}'.format(problem.name))
    task = grounding.ground(problem)
    logging.info('Grounding end: {0}'.format(problem.name))
    logging.info('{0} Variables created'.format(len(task.facts)))
    logging.info('{0} Operators created'.format(len(task.operators)))
    return task

def build_graph_causal(domain, task, save_graph=True):
    """ Build a causal graph from a tasl object, modified from original ptg.py
    to use networkx structure

    Args:
        task: Task object
        save_graph: Boolean, whether to save graph into .dot file
    Returns:
        graph: 
            node attributes:
                stuffs for plotting
                op_name
                manipuland
                is_subgoal
            edge attributes:
                reason for edge (transition condition / co-occuring effects)
                op_name 

    """
    graph = nx.DiGraph()

    action_dict = {}
    for a in domain.actions:
        for op in task.operators:
            if a in op.name:
                action_dict[op.name] = a
    
    pred_dict = {}
    for p in domain.predicates:
        for f in task.facts:
            if p in f:
                pred_dict[f] = p
    
    for op in task.operators:
        for prop in task.facts:
            if prop in op.preconditions:
                if pred_dict.get(prop) not in graph.nodes:
                    graph.add_node(pred_dict.get(prop))
                if action_dict.get(op.name) not in graph.nodes:
                    graph.add_node(action_dict.get(op.name))
                
                graph.add_edge(pred_dict.get(prop), action_dict.get(op.name))
            
            elif prop in op.add_effects or prop in op.del_effects:
                if pred_dict.get(prop) not in graph.nodes:
                    graph.add_node(pred_dict.get(prop))
                if action_dict.get(op.name) not in graph.nodes:
                    graph.add_node(action_dict.get(op.name))
                
                graph.add_edge(pred_dict.get(prop), action_dict.get(op.name))



