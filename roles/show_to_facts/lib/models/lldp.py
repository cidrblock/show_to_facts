""" the lldp model
"""
class Interface(): #pylint: disable=R0903
    """ the Interface class
    """
    def __init__(self):
        self.local = ""
        self.neighbor = ""

    def to_facts(self):
        """ return the interface as a dict
        """
        return {
            'local': self.local,
            'neighbor': self.neighbor
            }

class Neighbor(): #pylint: disable=R0903
    """ the neighbor class
    """
    def __init__(self):
        self.name = ""
        self.description = ""
        self.opersys = ""
        self.interfaces = []

    def to_facts(self):
        """ Return the neighbor as a dict
        """
        return {
            'name': self.name,
            'description': self.description,
            'os': self.opersys,
            'interfaces': self.interfaces
        }

class Neighbors():
    """ the neighbors class
    """
    def __init__(self):
        self._neighbors = {}

    def __iter__(self):
        yield self._neighbors

    def upsert(self, neighbor):
        """ upset a neighbor

        Arguments:
            neighbor (obj): A Neighbor

        Returns:
            Neighbor: A Neighbor instance
        """
        short_name = neighbor.name.split('.')[0]
        if short_name not in self._neighbors:
            self._neighbors[short_name] = neighbor
        else:
            self._neighbors[short_name].description = neighbor.description
            self._neighbors[short_name].opersys = neighbor.opersys
            self._neighbors[short_name].interfaces.extend(neighbor.interfaces)
        return self._neighbors[short_name]

    def _unique(self):
        return len(self._neighbors)

    def _total(self):
        return sum([len(neighbor.interfaces) for name, neighbor in self._neighbors.items()])

    def to_facts(self):
        """ Return the neighbors as a dict
        """
        return {
            "details": self._neighbors,
            "summary": {
                "total": self._total(),
                "unique": self._unique()
                }
            }

class Lldp(): #pylint: disable=R0903
    """ The lldp class
    """
    def __init__(self):
        self.neighbors = Neighbors()

    def to_facts(self):
        """ Return the lldp as a dict
        """
        return {
            'lldp': {
                'neighbors': self.neighbors
            }
        }
