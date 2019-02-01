# Copyright (c) 2018, Nokia

# This file contains functions used by the hooks to enable Nuage VSP
# in Openstack.

from collections import OrderedDict
from copy import deepcopy
import subprocess
import neutron_nuage_context
from charmhelpers.contrib.openstack import templating
from charmhelpers.contrib.openstack.neutron import neutron_plugin_attribute
from charmhelpers.fetch import (
    apt_install,

)
from charmhelpers.core.hookenv import (
    log,
    config,
    relation_set
)
from charmhelpers.contrib.openstack.utils import (
    os_release,
)

TEMPLATES = 'templates/'

NUAGE_PACKAGES = [
    'nuage-openstack-neutron',
    'nuage-openstack-neutronclient'
]

NEUTRON_CONF_DIR = "/etc/neutron"
SOURCES_LIST = '/etc/apt/sources.list'
NUAGE_CONF = '%s/plugins/nuage/nuage_plugin.ini' % NEUTRON_CONF_DIR

BASE_RESOURCE_MAP = OrderedDict([
    (NUAGE_CONF, {
        'services': ['neutron-server'],
        'contexts': [neutron_nuage_context.NeutronNuagePluginContext()],
    }),
])

def determine_packages():
    '''
    Returns list of packages required to be installed alongside neutron to
    enable Nuage VSP in Openstack.
    '''
    pkgs = []
    additional_packages = config('nuage-additional-packages')
    pkgs = NUAGE_PACKAGES + additional_packages.split(',')
    return pkgs



def register_configs(release=None):
    '''
    Returns an object of the Openstack Tempating Class which contains the
    the context required for all templates of this charm.
    '''
    release = release or os_release('neutron-common', base='kilo')
    if release < 'queens':
        raise ValueError('OpenStack %s release not supported' % release)

    configs = templating.OSConfigRenderer(templates_dir=TEMPLATES,
                                          openstack_release=release)
    for cfg, rscs in resource_map().iteritems():
        configs.register(cfg, rscs['contexts'])
    return configs


def restart_map():
    '''
    Constructs a restart map based on charm config settings and relation
    state.
    '''
    return OrderedDict([(cfg, v['services'])
                        for cfg, v in resource_map().iteritems()
                        if v['services']])

def resource_map():
    '''
    Dynamically generate a map of resources that will be managed for a single
    hook execution.
    '''
    resource_map = deepcopy(BASE_RESOURCE_MAP)
    is_legacy_mode = config('manage-neutron-plugin-legacy-mode')
    if is_legacy_mode:
        del resource_map[NUAGE_CONF]
    return resource_map


def _exec_cmd(cmd=None, error_msg='Command exited with ERRORs', fatal=False):
    '''
    Function to execute any bash command on the node.
    '''
    if cmd is None:
        log("No command specified")
    else:
        if fatal:
            subprocess.check_call(cmd)
        else:
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                log(error_msg)


def set_neutron_relation():
    settings = {
        'neutron-plugin': 'vsp',
        'core-plugin': neutron_plugin_attribute('vsp', 'driver',
                                                'neutron'),
        'neutron-plugin-config': neutron_plugin_attribute('vsp',
                                                          'config', 'neutron'),
        'service-plugins': ' ',
    }
    relation_set(relation_settings=settings)