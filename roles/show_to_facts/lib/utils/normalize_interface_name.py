import re

def normalize_interface_name(name, os=None):
    if not name:
        return
    
    if os == 'nxos':
        def _get_number(name):
            digits = ''
            for char in name:
                if char.isdigit() or char in '/.':
                    digits += char
            return digits

        if name.lower().startswith('et'):
            if_type = 'Ethernet'
        elif name.lower().startswith('vl'):
            if_type = 'Vlan'
        elif name.lower().startswith('lo'):
            if_type = 'loopback'
        elif name.lower().startswith('po'):
            if_type = 'port-channel'
        elif name.lower().startswith('nv'):
            if_type = 'nve'
        else:
            if_type = None

        number_list = name.split(' ')
        if len(number_list) == 2:
            number = number_list[-1].strip()
        else:
            number = _get_number(name)

        if if_type:
            proper_interface = if_type + number
        else:
            proper_interface = name

        return proper_interface
    
    elif os == 'ios':
        INTERFACE_NAMES = {
            'Gi': 'GigabitEthernet',
        }


        match = re.match('([a-zA-Z]*)', name)
        if match and match.group(1) in INTERFACE_NAMES:
            matched = match.group(1)
            name = name.replace(matched, INTERFACE_NAMES[matched])
        return name

    elif os == 'eos':
        INTERFACE_NAMES = {
            'Et': 'Ethernet',
            'Ma': 'Management',
            'Vl': 'Vlan',
            'Po': 'PortChannel'
        }

        match = re.match('([a-zA-Z]*)', name)
        if match and match.group(1) in INTERFACE_NAMES:
            matched = match.group(1)
            name = name.replace(matched, INTERFACE_NAMES[matched])
        return name

    return name

