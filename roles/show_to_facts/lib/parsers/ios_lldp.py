# (c) 2018, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
""" the lldp/ios parser
"""

from __future__ import (absolute_import, division, print_function)

import re
from models.lldp import Lldp, Neighbor, Interface
from utils.splitter import section_split
from utils.determine_os import determine_os
from utils.normalize_interface_name import normalize_interface_name

class ParserEngine(): #pylint: disable=R0903
    """ the lldp/ios parser
    """

    PARSER_METADATA = {"network_os": "ios",
                       "commands": [
                           "show lldp neighbors",
                           "show lldp neighbors detail",
                           ],
                       "resource": "lldp"}

    @staticmethod
    def _parse_name(neighbor):
        rstr = re.compile(r'System Name: (?P<name>\S+)')
        matches = [m.group('name') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_description(neighbor):
        rstr = re.compile(r'System Description: \n(?P<description>.*?)\n\n', re.S)
        matches = [m.group('description') for m in [rstr.search(neighbor)] if m]
        return matches[0] if matches else None

    @staticmethod
    def _parse_neighbor_line(line):
        match = re.match(r'^(?P<name>\S+)\s+(?P<local_interface>\S+)'
                         r'\s+(?P<hold_time>\d+)\s+(?P<capabilities>\S+)'
                         r'\s+(?P<neighbor_interface>\S+)', line)
        if match:
            neighbor = Neighbor()
            neighbor.name = match.group('name')
            interface = Interface()
            interface.local = normalize_interface_name(match.group('local_interface'), 'ios')
            interface.neighbor = match.group('neighbor_interface')
            neighbor.interfaces.append(interface)
            return neighbor
        return None

    def parse(self, texts):
        """ run the parser

        Arguments:
            texts (list): A list of command outputs matching the metadata commands

        """
        lldp = Lldp()
        text = texts[0]
        for line in text.splitlines():
            neighbor = self._parse_neighbor_line(line)
            if neighbor:
                lldp.neighbors.upsert(neighbor)
        text = texts[1]
        neighbors_text = section_split(r'^----(.*)', text.splitlines())
        if neighbors_text[0]:
            for neighbor_text in neighbors_text:
                neighbor_string = '\n'.join(neighbor_text[1])
                neighbor = Neighbor()
                neighbor.name = self._parse_name(neighbor_string)
                neighbor.description = self._parse_description(neighbor_string)
                neighbor.opersys = determine_os(neighbor.description)
                neighbor = lldp.neighbors.upsert(neighbor)
                for interface in neighbor.interfaces:
                    interface.neighbor = normalize_interface_name(interface.neighbor,
                                                                  neighbor.opersys)
        return lldp
