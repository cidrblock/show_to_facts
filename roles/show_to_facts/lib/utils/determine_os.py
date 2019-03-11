import re

OS_RES = {
    'ios': [r'Cisco IOS '],
    'nxos': [r'.*Nexus.*'],
    'eos': [r'.*Arista.*']
    }


def determine_os(description):
    for os, regexs in OS_RES.items():
        for regex in regexs:
            match = re.match(regex, description)
            if match:
                return os
    return 'unknown'
