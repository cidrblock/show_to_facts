# (c) 2018, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
""" the lldp/nxos parser
"""
from __future__ import (absolute_import, division, print_function)

import re
from models.lldp import Lldp, Neighbor, Interface
from utils.splitter import section_split
from utils.determine_os import determine_os
from utils.normalize_interface_name import normalize_interface_name

class ParserEngine(): #pylint: disable=R0903
    """ the lldp/nxos parser
    """

    PARSER_METADATA = {"network_os": "nxos",
                       "commands": ["show lldp neighbors detail"],
                       "resource": "lldp"}

    @staticmethod
    def _parse_name(neighbor):
        rstr = re.compile(r'System Name: (?P<name>\S+)')
        matches = [m.group('name') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_description(neighbor):
        rstr = re.compile(r'System Description: (?P<description>.*)Time', re.S)
        matches = [m.group('description') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_neighbor_int(neighbor):
        rstr = re.compile(r'Port id: (?P<neighbor_int>\S+)')
        matches = [m.group('neighbor_int') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_local_int(neighbor):
        rstr = re.compile(r'Local Port id: (?P<local_int>\S+)')
        matches = [m.group('local_int') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    def parse(self, texts):
        """ run the parser

        Arguments:
            texts (list): A list of command outputs matching the metadata commands

        """
        text = texts[0]
        lldp = Lldp()
        neighbors_text = section_split(r'^Chassis id: (.*)', text.splitlines())
        for neighbor_text in neighbors_text:
            neighbor_string = '\n'.join(neighbor_text[1])
            neighbor = Neighbor()
            neighbor.name = self._parse_name(neighbor_string)
            neighbor.description = self._parse_description(neighbor_string)
            neighbor.opersys = determine_os(neighbor.description)
            interface = Interface()
            interface.local = normalize_interface_name(self._parse_local_int(neighbor_string),
                                                       'nxos')
            interface.neighbor = normalize_interface_name(self._parse_neighbor_int(neighbor_string),
                                                          neighbor.opersys)
            neighbor.interfaces.append(interface)
            lldp.neighbors.upsert(neighbor)
        return lldp
