from charmhelpers.core.hookenv import (
    config,
    relation_ids,
    related_units,
    relation_get,
)
from charmhelpers.contrib.openstack import context
VLAN = 'vlan'
VXLAN = 'vxlan'
OVERLAY_NET_TYPES = [VXLAN]


class NeutronNuagePluginContext(context.NeutronContext):

    @property
    def plugin(self):
        '''
        Over-riding function in NeutronContext Class to return 'vsp'
        as the neutron plugin.
        '''
        return 'vsp'

    @property
    def network_manager(self):
        '''
        Over-riding function in NeutronContext Class to return 'neutron'
        as the network manager.
        '''
        return 'neutron'

    def _ensure_packages(self):
        '''
        Over-riding function in NeutronContext Class.
        Function only runs on compute nodes.
        '''
        pass

    def _save_flag_file(self):
        '''
        Over-riding function in NeutronContext Class.
        Function only needed for OVS.
        '''
        pass

    def nuage_ctxt(self):
        '''
        Generated Config for all Nuage VSP templates inside the
        templates folder.
        '''
        nuage_ctxt = super(NeutronNuagePluginContext, self).nuage_ctxt()
        if not nuage_ctxt:
            return {}

        conf = config()

        nuage_ctxt['vsd_cms_id'] = config('vsd-cms-id')
        nuage_ctxt['vsd_cms_name'] = config('vsd-cms-name')
        nuage_ctxt['vsd_server'] = config('vsd-server')
        nuage_ctxt['vsd_auth'] = config('vsd-auth')
        nuage_ctxt['vsd_organization'] = config('vsd-organization')
        nuage_ctxt['vsd_auth_ssl'] = config('vsd-auth-ssl')
        nuage_ctxt['vsd_base_uri'] = config('vsd-base-uri')
        nuage_ctxt['vsd_auth-resource'] = config('vsd-auth-resource')
        nuage_ctxt['vsd_netpart_name'] = config('vsd-netpart-name')
        nuage_ctxt['extension_drivers'] = config('extension-drivers')
        nuage_ctxt['type_drivers'] = config('type-drivers')
        nuage_ctxt['mechanism_drivers'] = config('mechanism_drivers')
        nuage_ctxt['service_plugins'] = config('service_plugins')


        return nuage_ctxt
