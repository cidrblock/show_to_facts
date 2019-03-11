""" the interfaces class
"""
import ipaddress

class State(): #pylint: disable=R0903
    """ The state class

    Attributes:
        administrative (str): The admin state
        operating (str): The oper state

    """
    def __init__(self, administrative=None, operating=None):
        self.administrative = administrative
        self.operating = operating
        self.brief = "%s_%s" % (self.administrative, self.operating)

    def to_facts(self):
        """ Return the state as a dict
        """
        return {"administrative": self.administrative,
                "operating": self.operating,
                "brief": self.brief}

class InterfaceIpv4Address(): #pylint: disable=R0903
    """ The interface ipv4 address class

    Arguments:
        address (str): The ipv4 address in 1.1.1.1/32 format

    """
    def __init__(self, address):
        self._address = address

    def to_facts(self):
        """ Return the ipv4 address as a dict
        """
        return {"address": str(ipaddress.ip_interface(self._address).ip),
                "network": str(ipaddress.ip_interface(self._address).network.network_address),
                "netmask": str(ipaddress.ip_interface(self._address).network.netmask),
                "prefix_length": str(ipaddress.ip_interface(self._address).network.prefixlen)
                }

class Interface(): #pylint: disable=R0903
    """ the interface class
    """
    def __init__(self):
        self.name = None
        self.hardware = None
        self.ipv4_address = None
        self.state = State()
        self.description = None

    def to_facts(self):
        """ Return the interface as a dict
        """
        return {"name": self.name,
                "description": self.description,
                "hardware": self.hardware,
                "ipv4_address": self.ipv4_address,
                "state": self.state}

class Interfaces():
    """ the interfaces class
    """
    def __init__(self):
        self._interfaces = {}

    def add(self, interface):
        """ add an interface

        Arguments:
            interface (obj): An Interface

        """
        self._interfaces[interface.name] = interface

    def _admin_up(self):
        return [v.name for k, v in self._interfaces.items() if v.state.administrative == "up"]

    def _admin_down(self):
        return [v.name for k, v in self._interfaces.items() if v.state.administrative == "down"]

    def _operating_up(self):
        return [v.name for k, v in self._interfaces.items() if v.state.operating == "up"]

    def _operating_down(self):
        return [v.name for k, v in self._interfaces.items() if v.state.operating == "down"]

    def _up_up(self):
        return [v.name for k, v in self._interfaces.items() if v.state.brief == "up_up"]

    def _up_down(self):
        return [v.name for k, v in self._interfaces.items() if v.state.brief == "up_down"]

    def _down_down(self):
        return [v.name for k, v in self._interfaces.items() if v.state.brief == "down_down"]

    def _down_up(self):
        return [v.name for k, v in self._interfaces.items() if v.state.brief == "down_up"]

    def _summary(self):
        return {"total": len(self._interfaces),

                "state": {
                    "administrative": {
                        "up": len(self._admin_up()),
                        "down": len(self._admin_down())
                    },
                    "operating": {
                        "up": len(self._operating_up()),
                        "down": len(self._operating_down())
                    },
                    "up_up": {
                        "total": len(self._up_up()),
                        "interfaces": self._up_up()
                    },
                    "up_down": {
                        "total": len(self._up_down()),
                        "interfaces": self._up_down()
                    },
                    "down_down": {
                        "total": len(self._down_down()),
                        "interfaces": self._down_down()
                    },
                    "down_up": {
                        "total": len(self._down_up()),
                        "interfaces": self._down_up()
                    }
                }}

    def to_facts(self):
        """ Return the interfaces as a dict
        """
        return {"interfaces": {
            "details": self._interfaces,
            "summary": self._summary()
            }
                }
