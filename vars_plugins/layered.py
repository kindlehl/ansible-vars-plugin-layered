import os
from ansible import constants as C
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.plugins.vars import BaseVarsPlugin
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.utils.vars import combine_vars

FOUND = {}


class VarsModule(BaseVarsPlugin):

    REQUIRES_WHITELIST = True

    def is_env(self, group):
        return str(group) in ['prod', 'stage', 'dev']

    def get_vars(self, loader, path, entities, cache=True):
        ''' parses the vars/<env>/<type>.yaml files  '''

        if not isinstance(entities, list):
            entities = [entities]

        if isinstance(entities[0], Host):
            return {}

        super(VarsModule, self).get_vars(loader, path, entities)

        data = {}
        # Grab name of first env group. If there is no env group for these entities, return empty vars
        try:
            envs = [str(e) for e in entities if self.is_env(e)]
            # Grab first environment name if for some reason there are two declared
            env = envs[0]
            # Remove env groups from entities
            entities = [e for e in entities if not self.is_env(e)]
        except:
            return data

        for entity in entities:
            if isinstance(entity, Group):
                subdir = 'vars/{}'.format(env)
            else:
                raise AnsibleParserError("Supplied entity must be Host or Group, got %s instead" % (type(entity)))

            # avoid 'chroot' type inventory hostnames /path/to/chroot
            if not entity.name.startswith(os.path.sep):
                try:
                    found_files = []
                    # load vars
                    b_opath = os.path.realpath(to_bytes(os.path.join(self._basedir, subdir)))
                    opath = to_text(b_opath)
                    key = '%s.%s' % (entity.name, opath)
                    if cache and key in FOUND:
                        found_files = FOUND[key]
                    else:
                        # no need to do much if path does not exist for basedir
                        if os.path.exists(b_opath):
                            if os.path.isdir(b_opath):
                                self._display.debug("\tprocessing dir %s" % opath)
                                # Find .yml and .yaml files
                                found_files = loader.find_vars_files(opath, entity.name + '.yml')
                                found_files += loader.find_vars_files(opath, entity.name + '.yaml')
                                FOUND[key] = found_files
                            else:
                                self._display.warning("Found %s that is not a directory, skipping: %s" % (subdir, opath))

                    for found in found_files:
                        new_data = loader.load_from_file(found, cache=True, unsafe=True)
                        if new_data:  # ignore empty files
                            data = combine_vars(data, new_data)

                except Exception as e:
                    raise AnsibleParserError(to_native(e))
        return data

