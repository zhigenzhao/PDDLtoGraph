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
import copy
import networkx as nx
import pygraphviz as pgv
from matplotlib import pyplot as plt

try:
    import argparse
except ImportError:
    from external import argparse

PTGPATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PTGPATH)

from pddl.parser import Parser
import tools
import grounding_orig as grounding

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

    return (domain, problem)

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

def build_graph_causal(task, show=True, add_cooccuring_edges=True):
    """ Build a causal graph from a tasl object, modified from original ptg.py
    to use networkx structure

    Args:
        task: Task object
        show_graph: Boolean, whether to show graph
        add_cooccuring_edges: Boolean, whether to add causal edges due to 
            co-occuring effects
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

    for u in task.facts:
        for v in task.facts:
            for op in task.operators:
                if u==v:
                    continue
                elif u in op.preconditions:
                    if v in op.add_effects or v in op.del_effects:
                        if u not in graph.nodes:
                            graph.add_node(u)
                        if v not in graph.nodes:
                            graph.add_node(v)
                        if u in op.add_effects or u in op.del_effects:
                            graph.add_edge(u, v, reason="transition & cooccuring")
                        else:
                            graph.add_edge(u, v, reason="transition")

                elif add_cooccuring_edges and (u in op.add_effects or u in op.del_effects):
                    if v in op.add_effects or v in op.del_effects:
                        if u not in graph.nodes:
                            graph.add_node(u)
                        if v not in graph.nodes:
                            graph.add_node(v)

                        graph.add_edge(u, v, reason="cooccuring") 

    if show:
        show_graph(graph)

    return graph

def cut_graph(G, node_list):
    graph = copy.deepcopy(G)

    for node in node_list:
        print("Removing node", node)
        try:
            graph.remove_node(node)
        except:
            print("Warning: node not found", node)

    return graph

def show_graph(graph):
    plt.subplot(111)
    nx.draw(graph, with_labels=True)
    plt.show()

def main():
    domain_file = "/home/zhigen/code/pddl_planning/examples/strips/conveyor_belt/domain_coupled.pddl"
    problem_file = "/home/zhigen/code/pddl_planning/examples/strips/conveyor_belt/2obj_coupled.pddl"       

    domain, problem = parse(domain_file, problem_file)
    task = ground(problem)

    graph = build_graph_causal(task, add_cooccuring_edges=True)

    clean_graph = cut_graph(graph, [
        "(free iiwa)", 
        "(unblocked box_0 box_0)",
        "(unblocked box_1 box_1)",
        ])
    show_graph(clean_graph)

if __name__=="__main__":
    main()

