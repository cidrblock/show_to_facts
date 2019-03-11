from __future__ import (absolute_import, division, print_function)

from models.interfaces import Interfaces, Interface, State, InterfaceIpv4Address
from utils.splitter import section_split
import re
import ipaddress
import json
__metaclass__ = type

class ParserEngine(object):

    PARSER_METADATA = {"network_os": "nxos", 
                       "commands": ["show interface"],
                       "resource": "interfaces"} 

    @staticmethod
    def parse_admin_state(interface):
        r = re.compile(r'admin state is (?P<admin_state>\w+)')
        matches = [m.group('admin_state') for m in [r.search(interface)] if m]
        return matches[0] if matches else None

    @staticmethod
    def parse_description(interface):
        r = re.compile(r'Description: (?P<description>.*)')
        matches = [m.group('description') for m in [r.search(interface)] if m]
        return matches[0] if matches else None

    @staticmethod
    def parse_ipv4_string(interface):
        r = re.compile(r'Internet Address is (?P<address>\S+)')
        matches = [m.group('address') for m in [r.search(interface)] if m]
        return matches[0] if matches else None
        
    @staticmethod
    def parse_hardware(interface):
        r = re.compile(r'Hardware: (?P<hardware>.*),')
        matches = [m.group('hardware') for m in [r.search(interface)] if m]
        return matches[0] if matches else None

    def parse(self, texts):
        text = texts[0]
        int_re = r'^(?P<name>\S+) is (?P<oper_state>\w+)'
        interfaces_text = section_split(int_re, text.splitlines())
        interfaces = Interfaces()
        for interface_text in interfaces_text:
            match = re.match(int_re, interface_text[0])
            interface = Interface()
            interface.name = match.group('name')
            interface_string = '\n'.join(interface_text[1])
            interface.state = State(administrative=self.parse_admin_state(interface_string),
                                    operating=match.group('oper_state'))
            interface.hardware = self.parse_hardware(interface_string)
            interface.description = self.parse_description(interface_string)
            ipv4_string = self.parse_ipv4_string(interface_string)
            if ipv4_string:
                interface.ipv4_address = InterfaceIpv4Address(ipv4_string)
            interfaces.add(interface)
        return interfaces
