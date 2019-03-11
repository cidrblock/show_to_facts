# (c) 2018, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
""" show to facts
"""
from __future__ import (absolute_import, division, print_function)

import os
import sys
import json

from ansible.plugins.action import ActionBase
from ansible.module_utils.connection import Connection, ConnectionError #pylint: disable=W0622
from ansible.module_utils._text import to_text
from ansible.errors import AnsibleError
from ansible.utils.display import Display

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir, 'lib'))
from parsers import parser_loader, ToFacts #pylint: disable=E0401,C0413

class ActionModule(ActionBase): #pylint: disable=R0903
    """ The action module class
    """
    display = Display()

    def _get_network_os(self, task_vars):
        if 'network_os' in self._task.args and self._task.args['network_os']:
            self.display.vvvv('Getting network OS from task argument')
            network_os = self._task.args['network_os']
        elif self._play_context.network_os:
            self.display.vvvv('Getting network OS from inventory')
            network_os = self._play_context.network_os
        elif ('network_os' in task_vars.get('ansible_facts', {}) and
              task_vars['ansible_facts']['network_os']):
            self.display.vvvv('Getting network OS from fact')
            network_os = task_vars['ansible_facts']['network_os']
        else:
            raise AnsibleError('ansible_network_os must be specified on this host.')
        return network_os

    def _get_os_resource(self, network_os, resource):
        parsers = [p for p in parser_loader.all() if p.PARSER_METADATA['network_os']
                   == network_os and p.PARSER_METADATA['resource'] == resource]
        if not parsers:
            self.display.warning("No parser available for resource %s for network os %s"
                                 % (resource, network_os))
            return None
        return parsers[0]

    def _run_command(self, command, task_vars):
        socket_path = getattr(self._connection, 'socket_path') or task_vars.get('ansible_socket')
        connection = Connection(socket_path)
        try:
            output = connection.get(command)
        except ConnectionError as exc:
            raise AnsibleError(to_text(exc))
        return output

    @staticmethod
    def _command_map():
        command_map = {}
        parsers = [p.PARSER_METADATA for p in parser_loader.all()]
        for parser in parsers:
            if not parser['resource'] in command_map:
                command_map[parser['resource']] = {}
            if not os in command_map[parser['resource']]:
                command_map[parser['resource']][parser['network_os']] = []
            command_map[parser['resource']][parser['network_os']].append(parser['commands'])
        return command_map

    @staticmethod
    def _validate_args(args):
        provided = set(list(args.keys()))
        valid_args = set(['resources', 'update_facts', 'fact_key', '_return_command_map'])
        extras = provided - valid_args
        if extras:
            raise AnsibleError("The following arguments are not supported: %s" % ','.join(extras))

    def run(self, tmp=None, task_vars=None):
        self.display.verbosity = self._play_context.verbosity

        self._validate_args(self._task.args)
        result = super(ActionModule, self).run(tmp, task_vars)
        if '_return_command_map' in self._task.args and self._task.args['_return_command_map']:
            result.update({
                'command_map': self._command_map()
                        })
            return result

        network_os = self._get_network_os(task_vars)

        facts = {}
        if 'resources' in self._task.args and self._task.args['resources']:
            resources = self._task.args['resources']
        else:
            resources = [p.PARSER_METADATA['resource'] for p in parser_loader.all()
                         if p.PARSER_METADATA['network_os'] == network_os]

        for resource in resources:
            if 'name' in resource:
                resource_name = resource['name']
            else:
                resource_name = resource

            parser = self._get_os_resource(network_os, resource_name)
            if parser:
                if 'output' in resource:
                    outputs = resource['output']
                else:
                    outputs = []
                    for command in parser.PARSER_METADATA['commands']:
                        outputs.append(self._run_command(command, task_vars))
                objs = parser.parse(outputs)
                facts.update(json.loads(json.dumps(objs, sort_keys=True, cls=ToFacts)))

        if 'update_facts' in self._task.args:
            result.update({
                'ansible_facts': {self._task.args['fact_key']: facts}
            })

        result.update({'results': facts})
        return result
