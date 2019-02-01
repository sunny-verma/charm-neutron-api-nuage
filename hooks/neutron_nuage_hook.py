import sys
from charmhelpers.core.hookenv import (
    Hooks,
    UnregisteredHookError,
    log,
    config,
    status_set
)

from charmhelpers.core.host import (
    restart_on_change,
    service_start,
    service_stop,
    service_running
)

from charmhelpers.fetch import (
    apt_install,
    apt_update,
    configure_sources,
)

from neutron_nuage_utils import (
    determine_packages,
    register_configs,
    restart_map,
    set_neutron_relation,
)

hooks = Hooks()
CONFIGS = register_configs()


@hooks.hook()
def install():
    '''
    Install hook is run when the charm is first deployed on a node.
    '''
    status_set('maintenance', 'Executing pre-install')
    configure_sources(config('nuage-extra-source'), config('nuage-extra-key'))
    status_set('maintenance', 'Installing apt packages')
    apt_update()
    pkgs = determine_packages()
    for pkg in pkgs:
        apt_install(pkg, options=['--force-yes', '--allow-unauthenticated'], fatal=True)


@hooks.hook('config-changed')
@restart_on_change(restart_map())
def config_changed():
    '''
    This hook is run when a config parameter is changed.
    It also runs on node reboot.
    '''
    charm_config = config()
    if ( charm_config.changed('nuage_extra_soruce') or
        charm_config.changed('nuage_extra_key')):
        configure_sources(config('nuage-extra-source'), config('nuage-extra-key'))

    if charm_config.changed('nuage_additional_packages'):
        status_set('maintenance', 'Upgrading apt packages')
        apt_update()
        pkgs = determine_packages()
        for pkg in pkgs:
            apt_install(pkg, options=['--force-yes', '--allow-unauthenticated'], fatal=True)
        service_stop('neutron-server')
    CONFIGS.write_all()
    if not service_running('neutron-server'):
        service_start('neutron-server')


@hooks.hook("neutron-plugin-api-subordinate-relation-joined")
def neutron_plugin_joined():
    set_neutron_relation()
    CONFIGS.write_all()


@hooks.hook('stop')
def stop():
    '''
    This hook is run when the charm is destroyed.
    '''
    log('Charm stopping without removal of packages')


@hooks.hook('update-status')
def update_status():
    if service_running('neutron-server'):
        status_set('active', 'Unit is ready')
    else:
        status_set('blocked', 'neutron server not running')


def main():
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))


if __name__ == '__main__':
    main()