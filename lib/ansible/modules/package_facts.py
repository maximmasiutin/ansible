#!/usr/bin/python
# (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# most of it copied from AWX's scan_packages module

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: package_facts
short_description: Package information as facts
description:
  - Return information about installed packages as facts.
options:
  manager:
    description:
      - The package manager used by the system so we can query the package information.
      - Since 2.8 this is a list and can support multiple package managers per system.
      - The 'portage' and 'pkg' options were added in version 2.8.
      - The 'apk' option was added in version 2.11.
      - The 'yum' option was added in version 2.12.
      - If both 'yum' and 'rpm' managers are found in the 'auto' mode, and the strategy is 'first',
        then the 'rpm' will have priority over the 'yum'
    default: ['auto']
    choices: ['auto', 'rpm', 'apt', 'portage', 'pkg', 'pacman', 'apk', 'yum']
    type: list
    elements: str
  strategy:
    description:
      - This option controls how the module queries the package managers on the system.
        C(first) means it will return only information for the first supported package manager available.
        C(all) will return information for all supported and available package managers on the system.
    choices: ['first', 'all']
    default: 'first'
    type: str
    version_added: "2.8"
  all_available:
    description:
      - This option returns all available packages rather then just the installed ones.
    type: bool
    default: 'no'
    version_added: "2.12"
  need_package_details:
    description:
      - If this option is set to 'no', then just the module name is returned for each module without any other pieces of information like version, etc.
    type: bool
    default: 'yes'
    version_added: "2.12"

version_added: "2.5"
requirements:
    - For 'portage' support it requires the C(qlist) utility, which is part of 'app-portage/portage-utils'.
    - For Debian-based systems C(python-apt) package must be installed on targeted hosts.
author:
  - Matthew Jones (@matburt)
  - Brian Coca (@bcoca)
  - Adam Miller (@maxamillion)
  - Maxim Masiutin (@maximmasiutin)
notes:
  - Supports C(check_mode).
'''

EXAMPLES = '''
- name: Gather the facts on installed packages
  ansible.builtin.package_facts:
    manager: auto

- name: Gather the list of all available packages, names only without details
  ansible.builtin.package_facts:
    all_available: yes
    need_package_details: no

- name: Print the package facts
  ansible.builtin.debug:
    var: ansible_facts.packages

- name: Check whether a package called foobar is installed
  ansible.builtin.debug:
    msg: "{{ ansible_facts.packages['foobar'] | length }} versions of foobar are installed!"
  when: "'foobar' in ansible_facts.packages"

'''

RETURN = '''
ansible_facts:
  description: Facts to add to ansible_facts.
  returned: always
  type: complex
  contains:
    packages:
      description:
        - Maps the package name to a non-empty list of dicts with package information.
        - Every dict in the list corresponds to one installed version of the package.
        - The fields described below are present for all package managers. Depending on the
          package manager, there might be more fields for a package.
        - Is returned when the operating system level package manager is specified or auto detected manager
      returned: when the 'all_available' option is 'no' (by default) and the operating system level package manager is specified or auto detected manager
      type: dict
      contains:
        name:
          description: The package's name.
          returned: always
          type: str
        version:
          description: The package's version.
          returned: always
          type: str
        source:
          description: Where information on the package came from.
          returned: always
          type: str
      sample: |-
        {
          "packages": {
            "kernel": [
              {
                "name": "kernel",
                "source": "rpm",
                "version": "3.10.0",
                ...
              },
              {
                "name": "kernel",
                "source": "rpm",
                "version": "3.10.0",
                ...
              },
              ...
            ],
            "kernel-tools": [
              {
                "name": "kernel-tools",
                "source": "rpm",
                "version": "3.10.0",
                ...
              }
            ],
            ...
          }
        }
        # Sample rpm
        {
          "packages": {
            "kernel": [
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel",
                "release": "514.26.2.el7",
                "source": "rpm",
                "version": "3.10.0"
              },
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel",
                "release": "514.16.1.el7",
                "source": "rpm",
                "version": "3.10.0"
              },
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel",
                "release": "514.10.2.el7",
                "source": "rpm",
                "version": "3.10.0"
              },
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel",
                "release": "514.21.1.el7",
                "source": "rpm",
                "version": "3.10.0"
              },
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel",
                "release": "693.2.2.el7",
                "source": "rpm",
                "version": "3.10.0"
              }
            ],
            "kernel-tools": [
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel-tools",
                "release": "693.2.2.el7",
                "source": "rpm",
                "version": "3.10.0"
              }
            ],
            "kernel-tools-libs": [
              {
                "arch": "x86_64",
                "epoch": null,
                "name": "kernel-tools-libs",
                "release": "693.2.2.el7",
                "source": "rpm",
                "version": "3.10.0"
              }
            ],
          }
        }
        # Sample deb
        {
          "packages": {
            "libbz2-1.0": [
              {
                "version": "1.0.6-5",
                "source": "apt",
                "arch": "amd64",
                "name": "libbz2-1.0"
              }
            ],
            "patch": [
              {
                "version": "2.7.1-4ubuntu1",
                "source": "apt",
                "arch": "amd64",
                "name": "patch"
              }
            ],
          }
        }
    available_packages:
      description:
        - Same as 'packages' (see above) but contains the list of all available packages
          rather than the list of installed ones
      returned: when the 'all_available' option is set to 'yes'
      type: dict
      contains:
        name:
          description: The package's name.
          returned: always
          type: str
        is_installed:
          description: Whether the package is installed
          returned: when need_package_details option is 'yes' (default)
          type: bool

'''

import re

from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.respawn import (has_respawned,
                                                 probe_interpreters_for_module,
                                                 respawn_module)
from ansible.module_utils.facts.packages import LibMgr, CLIMgr, get_all_pkg_managers


class RPM(LibMgr):

    LIB = 'rpm'

    def list_installed(self):
        return self._lib.TransactionSet().dbMatch()

    def get_package_details(self, package):
        res = dict(name=package[self._lib.RPMTAG_NAME])
        if self._need_package_details:
            res.update(dict(
                version=package[self._lib.RPMTAG_VERSION],
                release=package[self._lib.RPMTAG_RELEASE],
                epoch=package[self._lib.RPMTAG_EPOCH],
                arch=package[self._lib.RPMTAG_ARCH],
            ))
        return res

    def is_available(self):
        ''' The RPM library does only read from the database of locally installed packages,
        not those available to download'''

        if self._all_available:
            return False

        # we expect the python bindings installed,
        # but this gives warning if they are missing and we have rpm cli
        we_have_lib = super(RPM, self).is_available()

        try:
            get_bin_path('rpm')

            if not we_have_lib and not has_respawned():
                # try to locate an interpreter with the necessary lib
                interpreters = ['/usr/libexec/platform-python',
                                '/usr/bin/python3',
                                '/usr/bin/python2']
                interpreter_path = probe_interpreters_for_module(interpreters, self.LIB)
                if interpreter_path:
                    respawn_module(interpreter_path)
                    # end of the line for this process;
                    # this module will exit when the respawned copy completes

            if not we_have_lib:
                module.warn('Found "rpm" but %s' % (missing_required_lib(self.LIB)))
        except ValueError:
            pass

        return we_have_lib


class APT(LibMgr):

    LIB = 'apt'

    def __init__(self):
        self._cache = None
        super(APT, self).__init__()

    @property
    def pkg_cache(self):
        if self._cache is not None:
            return self._cache

        self._cache = self._lib.Cache()
        return self._cache

    def is_available(self):
        ''' we expect the python bindings installed,
        but if there is apt/apt-get give warning about missing bindings'''
        we_have_lib = super(APT, self).is_available()
        if not we_have_lib:
            for exe in ('apt', 'apt-get', 'aptitude'):
                try:
                    get_bin_path(exe)
                except ValueError:
                    continue
                else:
                    if not has_respawned():
                        # try to locate an interpreter with the necessary lib
                        interpreters = ['/usr/bin/python3',
                                        '/usr/bin/python2']
                        interpreter_path = probe_interpreters_for_module(interpreters, self.LIB)
                        if interpreter_path:
                            respawn_module(interpreter_path)
                            # end of the line for this process;
                            # this module will exit here when respawned copy completes

                    module.warn('Found "%s" but %s' % (exe, missing_required_lib('apt')))
                    break

        return we_have_lib

    def list_installed(self):
        # Store the cache to avoid running pkg_cache()
        # for each item in the comprehension, which is very slow
        cache = self.pkg_cache
        return [pk for pk in cache.keys() if self._all_available or cache[pk].is_installed]

    def get_package_details(self, package):
        if not self._need_package_details:
            return dict(name=package)
        pkg_data = self.pkg_cache[package]
        res = dict(name=package)
        if self._all_available:
            res.update(dict(is_installed=pkg_data.is_installed))
        else:
            ac_pkg = pkg_data.installed
            res.update(dict(version=ac_pkg.version, arch=ac_pkg.architecture, category=ac_pkg.section, origin=ac_pkg.origins[0].origin))
        return res


class PACMAN(CLIMgr):

    CLI = 'pacman'

    def list_installed(self):
        return_code, out, err = module.run_command([self._cli, '-Qi'], environ_update=dict(LC_ALL='C'))
        if return_code != 0 or err:
            raise Exception("Unable to list packages rc=%s : %s" % (return_code, err))
        return out.split("\n\n")[:-1]

    def get_package_details(self, package):
        # parse values of details that might extend over several lines
        raw_pkg_details = {}
        last_detail = None
        for line in package.splitlines():
            matches = re.match(r"([\w ]*[\w]) +: (.*)", line)
            if matches:
                last_detail = matches.group(1)
                raw_pkg_details[last_detail] = matches.group(2)
            else:
                # append value to previous detail
                raw_pkg_details[last_detail] = raw_pkg_details[last_detail] + "  " + line.lstrip()

        provides = None
        if raw_pkg_details['Provides'] != 'None':
            provides = [
                p.split('=')[0]
                for p in raw_pkg_details['Provides'].split('  ')
            ]

        return {
            'name': raw_pkg_details['Name'],
            'version': raw_pkg_details['Version'],
            'arch': raw_pkg_details['Architecture'],
            'provides': provides,
        }


class PKG(CLIMgr):

    CLI = 'pkg'
    atoms = ['name', 'version', 'origin', 'installed', 'automatic', 'arch', 'category', 'prefix', 'vital']

    def list_installed(self):
        return_code, out, err = module.run_command([self._cli, 'query', "%%%s" % '\t%'.join(['n', 'v', 'R', 't', 'a', 'q', 'o', 'p', 'V'])])
        if return_code != 0 or err:
            raise Exception("Unable to list packages rc=%s : %s" % (return_code, err))
        return out.splitlines()

    def get_package_details(self, package):

        pkg = dict(zip(self.atoms, package.split('\t')))

        if 'arch' in pkg:
            try:
                pkg['arch'] = pkg['arch'].split(':')[2]
            except IndexError:
                pass

        if 'automatic' in pkg:
            pkg['automatic'] = bool(int(pkg['automatic']))

        if 'category' in pkg:
            pkg['category'] = pkg['category'].split('/', 1)[0]

        if 'version' in pkg:
            if ',' in pkg['version']:
                pkg['version'], pkg['port_epoch'] = pkg['version'].split(',', 1)
            else:
                pkg['port_epoch'] = 0

            if '_' in pkg['version']:
                pkg['version'], pkg['revision'] = pkg['version'].split('_', 1)
            else:
                pkg['revision'] = '0'

        if 'vital' in pkg:
            pkg['vital'] = bool(int(pkg['vital']))

        return pkg


class PORTAGE(CLIMgr):

    CLI = 'qlist'
    atoms = ['category', 'name', 'version', 'ebuild_revision', 'slots', 'prefixes', 'sufixes']

    def list_installed(self):
        return_code, out, err = module.run_command(' '.join([self._cli, '-Iv', '|', 'xargs', '-n', '1024', 'qatom']), use_unsafe_shell=True)
        if return_code != 0:
            raise RuntimeError("Unable to list packages rc=%s : %s" % (return_code, to_native(err)))
        return out.splitlines()

    def get_package_details(self, package):
        return dict(zip(self.atoms, package.split()))


class APK(CLIMgr):

    CLI = 'apk'

    def list_installed(self):
        if self._all_available:
            first_param = 'list'
            second_param = '-q'
        else:
            first_param = 'info'
            second_param = '-v'
        return_code, out, err = module.run_command([self._cli, first_param, second_param])
        if return_code != 0 or err:
            raise Exception("Unable to list packages rc=%s : %s" % (return_code, err))
        return out.splitlines()

    def get_package_details(self, package):
        splitted = package.split(' ')
        spl_first = splitted[0]
        nvr = spl_first.rsplit('-', 2)
        ret = {'name': nvr[0]}
        if self._need_package_details:
            if len(nvr) > 1:
                ret['version'] = nvr[1]
            if len(nvr) > 2:
                ret['release'] = nvr[2]
            if self._all_available:
                ret['installed'] = (splitted[-1] == '[installed]')
        return ret


class YUM(CLIMgr):

    CLI = 'yum'

    def __init__(self):
        self._compiled_re = None
        super(YUM, self).__init__()

    def list_installed(self):
        cmdparam = dict([(True, '--all'), (False, '--installed')])
        return_code, out, err = module.run_command([self._cli, 'list', '-q', cmdparam[self._all_available]])
        if return_code != 0 or err:
            raise Exception("Unable to list packages rc=%s : %s" % (return_code, err))
        return out.splitlines()

    def get_package_details(self, package):
        if self._compiled_re is None:
            self._compiled_re = re.compile(r'^\s*([-a-zA-Z0-9_.+]+)\s+([-a-zA-Z0-9_:.+~]+)\s+([-a-zA-Z0-9_:@]+)\s*$', flags=re.IGNORECASE)
        matches = self._compiled_re.match(package)
        if not matches:
            return dict()
        res = dict()
        first = matches.group(1)
        # use the rsplit and split and a simpler RegEx above (without backtracking) to avoid ReDoS attacks
        arch_list = first.rsplit('.', 1)
        if len(arch_list) == 2:
            pkg = arch_list[0]
            arch = arch_list[1]
        else:
            pkg = first
            arch = ''
        res['name'] = pkg
        if not self._need_package_details:
            return res
        if arch:
            res['arch'] = arch
        ver_full = matches.group(2)
        ver_list = ver_full.split(':', 1)
        if len(ver_list) == 2:
            epoch = ver_list[0]
            ver_tail = ver_list[1]
        else:
            epoch = ''
            ver_tail = ver_full
        if epoch:
            res['epoch'] = epoch
        ver_list = ver_tail.rsplit('-', 1)
        if len(ver_list) == 2:
            ver = ver_list[0]
            release = ver_list[1]
        else:
            ver = ver_tail
            release = ''
        if release:
            res['release'] = release
        res['version'] = ver
        res['repo'] = matches.group(3)
        return res


def main():

    # get supported pkg managers
    package_managers = get_all_pkg_managers()
    package_manager_names = [x.lower() for x in package_managers.keys()]

    # start work
    global module
    module = AnsibleModule(argument_spec=dict(manager={'type': 'list', 'elements': 'str', 'default': ['auto']},
                                              strategy={'choices': ['first', 'all'], 'default': 'first'},
                                              all_available=dict(type='bool', default=False),
                                              need_package_details=dict(type='bool', default=True)),
                           supports_check_mode=True)
    packages = {}
    results = {'ansible_facts': {}}
    managers = [x.lower() for x in module.params['manager']]
    strategy = module.params['strategy']
    auto = 'auto' in managers

    if auto:
        # keep order from user, we do dedupe below
        managers.extend(package_manager_names)
        managers.remove('auto')

    unsupported = set(managers).difference(package_manager_names)
    if unsupported:
        if 'auto' in module.params['manager']:
            msg = 'Could not auto detect a usable package manager, check warnings for details.'
        else:
            msg = 'Unsupported package managers requested: %s' % (', '.join(unsupported))
        module.fail_json(msg=msg)

    # If both "yum" and "rpm" managers are found in "auto" mode with the "first" strategy,
    # the "rpm" will have priority over "yum"
    higher_priority = 'rpm'
    lower_priority = 'yum'
    if auto and higher_priority in managers and lower_priority in managers and strategy == 'first':
        managers.remove(higher_priority)
        managers.insert(0, higher_priority)

    found = 0
    seen = set()
    for pkgmgr in managers:

        if found and strategy == 'first':
            break

        # dedupe as per above
        if pkgmgr in seen:
            continue
        seen.add(pkgmgr)
        try:
            try:
                # manager throws exception on init (calls self.test) if not usable.
                manager = package_managers[pkgmgr]()
                manager.set_package_details(module.params['need_package_details'])
                manager.set_all_available(module.params['all_available'])

                if manager.is_available():
                    found += 1
                    packages.update(manager.get_packages())

            except Exception as exc_inner:
                if pkgmgr in module.params['manager']:
                    module.warn('Requested package manager %s was not usable by this module: %s' % (pkgmgr, to_text(exc_inner)))
                continue

        except Exception as exc_outer:
            if pkgmgr in module.params['manager']:
                module.warn('Failed to retrieve packages with %s: %s' % (pkgmgr, to_text(exc_outer)))

    if found == 0:
        msg = ('Could not detect a supported package manager from the following list: %s, '
               'or the required Python library is not installed. Check warnings for details.' % managers)
        module.fail_json(msg=msg)

    # Set the facts, this will override the facts in ansible_facts that might exist from previous runs
    # when using operating system level or distribution package managers
    result_name = dict([(True, 'available_packages'), (False, 'packages')])
    results['ansible_facts'][result_name[module.params['all_available']]] = packages

    module.exit_json(**results)


if __name__ == '__main__':
    main()
