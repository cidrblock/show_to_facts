""" the eos/lldp parser
"""

from __future__ import (absolute_import, division, print_function)

import re
from models.lldp import Lldp, Neighbor, Interface
from utils.splitter import section_split
from utils.determine_os import determine_os
from utils.normalize_interface_name import normalize_interface_name

class ParserEngine(): #pylint: disable=R0903
    """ The eos/lldp parser
    """

    PARSER_METADATA = {"network_os": "eos",
                       "commands": ["show lldp neighbors detail"],
                       "resource": "lldp"}

    @staticmethod
    def _parse_name(neighbor):
        rstr = re.compile(r'System Name: "(?P<name>\S+)"')
        matches = [m.group('name') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_description(neighbor):
        rstr = re.compile(r'System Description: "(?P<description>.*?)"', re.S)
        matches = [m.group('description') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_neighbor_int(neighbor):
        rstr = re.compile(r'Port ID\s+: "(?P<neighbor_int>.*)"')
        matches = [m.group('neighbor_int') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    def parse(self, texts):
        """ run the parser

        Arguments:
            texts (list): A list of command outputs matching the metadata commands

        """
        text = texts[0]
        lldp = Lldp()
        li_re = r'^Interface (?P<local_interface>\S+)'
        local_interfaces = section_split(li_re, text.splitlines())
        for local_interface in local_interfaces:
            int_name = re.match(li_re, local_interface[0]).group('local_interface')
            neighbors_text = section_split(r'^  Neighbor', local_interface[1])
            for neighbor_text in neighbors_text:
                neighbor_string = '\n'.join(neighbor_text[1])
                neighbor = Neighbor()
                neighbor.name = self._parse_name(neighbor_string)
                neighbor.description = self._parse_description(neighbor_string)
                neighbor.opersys = determine_os(neighbor.description)
                interface = Interface()
                interface.local = normalize_interface_name(int_name, 'eos')
                interface.neighbor = normalize_interface_name(self._parse_neighbor_int(
                    neighbor_string),
                                                              neighbor.opersys)
                neighbor.interfaces.append(interface)
                lldp.neighbors.upsert(neighbor)
        return lldp
