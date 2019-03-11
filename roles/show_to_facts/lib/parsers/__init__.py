# (c) 2018, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.loader import PluginLoader
import json


parser_loader = PluginLoader(
    'ParserEngine',
    'parsers',
    None,
    'show_to_facts_parsers')

class ToFacts(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'to_facts'):
            return obj.to_facts()
        else:
            return json.JSONEncoder.default(self, obj)
